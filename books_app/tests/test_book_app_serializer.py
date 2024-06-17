from decimal import Decimal
from django.test import TestCase
from books_app.models import Book
from books_app.serializers import BookSerializer, BookListSerializer


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
