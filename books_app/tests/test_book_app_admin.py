from django.contrib.admin.sites import site
from django.test import TestCase
from books_app.models import Book


class BookAdminTest(TestCase):
    def test_book_admin_registered(self):
        self.assertIn(Book, site._registry)
