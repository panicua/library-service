from django.db import transaction
from rest_framework import serializers

from books_app.serializers import BookSerializer
from borrowing_app.models import Borrowing
from user.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("expected_return_date", "book")

    @staticmethod
    def validate_book(value):
        if value.inventory <= 0:
            raise serializers.ValidationError("You can't borrow a book now")
        return value

    def create(self, validated_data):
        with transaction.atomic():
            book = validated_data["book"]
            borrowing = Borrowing.objects.create(**validated_data)
            book.inventory -= 1
            book.save()
            return borrowing


class BorrowingListSerializer(BorrowingSerializer):
    user = UserSerializer(read_only=True)
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )
