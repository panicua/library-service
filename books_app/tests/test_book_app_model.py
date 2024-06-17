from decimal import Decimal
from django.test import TestCase
from books_app.models import Book


class BookModelTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover=Book.CoverType.SOFT,
            inventory=10,
            daily_fee=Decimal("1.99")
        )

    def test_book_creation(self):
        self.assertEqual(self.book.title, "Test Book")
        self.assertEqual(self.book.author, "Test Author")
        self.assertEqual(self.book.cover, Book.CoverType.SOFT)
        self.assertEqual(self.book.inventory, 10)
        self.assertEqual(self.book.daily_fee, Decimal("1.99"))

    def test_str_representation(self):
        self.assertEqual(str(self.book), "Test Book (Test Author)")
