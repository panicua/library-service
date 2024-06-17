from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from books_app.models import Book

User = get_user_model()


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
