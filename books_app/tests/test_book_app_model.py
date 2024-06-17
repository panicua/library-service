from decimal import Decimal
from django.core.exceptions import ValidationError
from django.test import TestCase
from books_app.models import Book


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
