from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from books_app.models import Book

User = get_user_model()


class BookAppViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(email='test@test.com', password='testpassword')
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.list_url = reverse('books_app:book-list')
        self.detail_url = lambda id: reverse('books_app:book-detail', args=[id])

    def test_create_book(self):
        data = {"title": "New Book", "author": "Author", "cover": "SOFT", "inventory": 1, "daily_fee": "0.02"}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_book(self):
        book = Book.objects.create(title="New Book", author="Author", cover="SOFT", inventory=1, daily_fee="0.02")
        response = self.client.delete(self.detail_url(book.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_book(self):
        book = Book.objects.create(title="New Book", author="Author", cover="SOFT", inventory=1, daily_fee="0.02")
        data = {"title": "Updated Book", "author": "Updated Author", "cover": "HARD", "inventory": 5, "daily_fee": "0.05"}
        response = self.client.put(self.detail_url(book.id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_books(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_book(self):
        book = Book.objects.create(title="New Book", author="Author", cover="SOFT", inventory=1, daily_fee="0.02")
        response = self.client.get(self.detail_url(book.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


