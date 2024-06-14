from rest_framework import serializers

from books_app.serializers import BookSerializer
from borrowing_app.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ["id", "borrow_date", "expected_return_date", "actual_return_date", "books", "user"]


class BorrowingListSerializer(BorrowingSerializer):
    reader_email = serializers.EmailField(source="user.email", read_only=True)
    books = serializers.SlugRelatedField(many=True, read_only=True, slug_field='title')

    class Meta:
        model = Borrowing
        fields = ["id", "borrow_date", "expected_return_date", "actual_return_date", "books", "reader_email"]


class BorrowingDetailSerializer(BorrowingSerializer):
    books = BookSerializer(many=True, read_only=True)
    reader_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Borrowing
        fields = ["id", "borrow_date", "expected_return_date", "actual_return_date", "books", "reader_email"]
