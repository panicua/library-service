from django.contrib.admin.sites import site
from django.test import TestCase
from books_app.models import Book
from decimal import Decimal
from django.core.exceptions import ValidationError
from books_app.serializers import BookSerializer, BookListSerializer
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse

User = get_user_model()


# BookAdminTest
class BookAdminTest(TestCase):
    def test_book_admin_registered(self):
        self.assertIn(Book, site._registry)


# BookModelTest
class BookModelTest(TestCase):
    def setUp(self):
        """Set up a book instance for testing the model."""
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover=Book.CoverType.SOFT,
            inventory=10,
            daily_fee=Decimal("1.99")
        )

    def test_book_creation(self):
        """Test the creation of a book instance."""
        self.assertEqual(self.book.title, "Test Book")
        self.assertEqual(self.book.author, "Test Author")
        self.assertEqual(self.book.cover, Book.CoverType.SOFT)
        self.assertEqual(self.book.inventory, 10)
        self.assertEqual(self.book.daily_fee, Decimal("1.99"))

    def test_str_representation(self):
        """Test the string representation of a book instance."""
        self.assertEqual(str(self.book), "Test Book (Test Author)")

    def test_inventory_positive(self):
        """Test that inventory is positive."""
        book = Book(
            title="Test Book",
            author="Test Author",
            cover=Book.CoverType.SOFT,
            inventory=-1,
            daily_fee=Decimal("1.99")
        )
        with self.assertRaises(ValidationError):
            book.full_clean()

    def test_daily_fee_positive(self):
        """Test that daily fee is positive."""
        book = Book(
            title="Test Book",
            author="Test Author",
            cover=Book.CoverType.SOFT,
            inventory=10,
            daily_fee=Decimal("-1.99")
        )
        with self.assertRaises(ValidationError):
            book.full_clean()


# BookSerializerTest
class BookSerializerTest(TestCase):
    def setUp(self):
        """Set up a book instance for testing serializers."""
        self.book_attributes = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": Book.CoverType.SOFT,
            "inventory": 10,
            "daily_fee": Decimal("1.99")
        }
        self.book = Book.objects.create(**self.book_attributes)

    def test_book_serializer(self):
        """Test the BookSerializer for the correct output data."""
        serializer = BookSerializer(self.book)
        data = serializer.data
        self.assertEqual(set(data.keys()), set(["id", "title", "author", "cover", "inventory", "daily_fee"]))
        self.assertEqual(data["title"], self.book_attributes["title"])
        self.assertEqual(data["author"], self.book_attributes["author"])
        self.assertEqual(data["cover"], self.book_attributes["cover"])
        self.assertEqual(data["inventory"], self.book_attributes["inventory"])
        self.assertEqual(data["daily_fee"], str(self.book_attributes["daily_fee"]))

    def test_book_list_serializer(self):
        """Test the BookListSerializer for the correct output data."""
        serializer = BookListSerializer(self.book)
        data = serializer.data
        self.assertEqual(set(data.keys()), set(["id", "title", "author", "inventory", "daily_fee"]))
        self.assertEqual(data["title"], self.book_attributes["title"])
        self.assertEqual(data["author"], self.book_attributes["author"])
        self.assertEqual(data["inventory"], self.book_attributes["inventory"])
        self.assertEqual(data["daily_fee"], str(self.book_attributes["daily_fee"]))


# UnauthenticatedBookAPITests
class UnauthenticatedBookAPITests(APITestCase):
    def setUp(self):
        """Set up the client and URLs for testing."""
        self.client = APIClient()
        self.list_url = reverse('books_app:book-list')
        self.detail_url = lambda id: reverse('books_app:book-detail', args=[id])

    def test_list_books(self):
        """Test that unauthenticated users can view the list of books."""
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


# AuthenticatedBookAPITests
class AuthenticatedBookAPITests(APITestCase):
    def setUp(self):
        """Set up the client, create a user, and authenticate the client."""
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            email='test@test.com',
            password='testpassword'
        )
        self.client.force_authenticate(self.user)

        self.list_url = reverse('books_app:book-list')
        self.detail_url = lambda id: reverse('books_app:book-detail', args=[id])

    def test_create_book(self):
        """Test that authenticated users can create books."""
        data = {"title": "New Book", "author": "Author", "cover": "SOFT", "inventory": 1, "daily_fee": "0.02"}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_book(self):
        """Test that authenticated users can delete books."""
        book = Book.objects.create(title="New Book", author="Author", cover="SOFT", inventory=1, daily_fee="0.02")
        response = self.client.delete(self.detail_url(book.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_book(self):
        """Test that authenticated users can update books."""
        book = Book.objects.create(title="New Book", author="Author", cover="SOFT", inventory=1, daily_fee="0.02")
        data = {"title": "Updated Book", "author": "Updated Author", "cover": "HARD", "inventory": 5, "daily_fee": "0.05"}
        response = self.client.put(self.detail_url(book.id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_books(self):
        """Test that authenticated users can view the list of books."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_book(self):
        """Test that authenticated users can retrieve a book by its ID."""
        book = Book.objects.create(title="New Book", author="Author", cover="SOFT", inventory=1, daily_fee="0.02")
        response = self.client.get(self.detail_url(book.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
