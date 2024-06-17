from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from borrowing_app.models import Borrowing
from books_app.models import Book
from payment_app.models import Payment

User = get_user_model()
BORROWING_URL = reverse("borrowing_app:borrowing-list")


class UnauthenticatedBorrowingTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated(self):
        response = self.client.get(BORROWING_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@test.test", password="passwordQq1"
        )
        self.client.force_authenticate(user=self.user)
        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            cover=Book.CoverType.SOFT,
            inventory=10,
            daily_fee=Decimal("1.00"),
        )

    def test_borrow_book_success(self):
        payload = {
            "expected_return_date": (date.today() + timedelta(days=7)).isoformat(),
            "book": self.book.id,
        }
        response = self.client.post(BORROWING_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertIn("book", response.data)

        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 9)

        borrowing = Borrowing.objects.get(id=response.data["book"])
        self.assertEqual(borrowing.book.id, self.book.id)
        self.assertEqual(borrowing.user.id, self.user.id)

    def test_borrow_book_no_inventory(self):
        self.book.inventory = 0
        self.book.save()
        payload = {
            "expected_return_date": (date.today() + timedelta(days=7)).isoformat(),
            "book": self.book.id,
        }
        response = self.client.post(BORROWING_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_book_success(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=7),
        )
        PAYMENT_URL = reverse(
            "borrowing_app:borrowing-return-book", args=[borrowing.id]
        )

        response = self.client.post(PAYMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        borrowing.refresh_from_db()
        self.assertEqual(borrowing.actual_return_date, date.today())

        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 11)

        payment = Payment.objects.get(borrowing=borrowing)
        self.assertEqual(payment.money_to_pay, borrowing.payable)

    def test_get_borrowings_authenticated_user(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=7),
        )
        response = self.client.get(BORROWING_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], borrowing.id)

    def test_get_borrowings_other_user(self):
        other_user = User.objects.create_user(
            email="other@test.test", password="passwordQq1"
        )
        Borrowing.objects.create(
            user=other_user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=7),
        )
        response = self.client.get(BORROWING_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_borrowings_staff_user(self):
        staff_user = User.objects.create_user(
            email="staff@test.test", password="passwordQq1", is_staff=True
        )
        self.client.force_authenticate(user=staff_user)
        Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=7),
        )
        response = self.client.get(BORROWING_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_borrowings_filter_by_active(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=7),
        )
        response = self.client.get(BORROWING_URL, {"is_active": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], borrowing.id)

        borrowing.actual_return_date = date.today()
        borrowing.save()

        response = self.client.get(BORROWING_URL, {"is_active": "false"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], borrowing.id)
