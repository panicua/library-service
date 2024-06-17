from datetime import date

from django.db import transaction
from rest_framework import serializers

from books_app.serializers import BookSerializer
from borrowing_app.models import Borrowing
from payment_app.serializers import PaymentSerializer
from user.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("expected_return_date", "book")

    @staticmethod
    def validate_book(value):
        if value.inventory <= 0:
            raise serializers.ValidationError(
                "There are no books left in inventory"
            )
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
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payment",
        )


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "actual_return_date", "expected_return_date", "borrow_date")
        read_only_fields = (
            "id",
            "actual_return_date",
            "expected_return_date",
            "borrow_date",
        )

    def validate(self, attrs):
        borrowing = self.instance
        if borrowing.actual_return_date is not None:
            raise serializers.ValidationError(
                "This borrowing has already been returned."
            )
        return attrs

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance.actual_return_date = date.today()
            instance.save()
            book = instance.book
            book.inventory += 1
            book.save()
            return instance
