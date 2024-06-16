from rest_framework import viewsets

from borrowing_app.models import Borrowing
from borrowing_app.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
)
from .tasks import send_telegram_message


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return BorrowingListSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)

        message = (
            f"*User*: {self.request.user},\n"
            f"*Borrowed book*: {instance.book.title},\n"
            f"*On date*: {instance.borrow_date},\n"
            f"*With expected return on*: {instance.expected_return_date}."
        )
        send_telegram_message.delay(message)
