from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from borrowing_app.models import Borrowing
from borrowing_app.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
)
from .tasks import send_telegram_message


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user

        if not user.is_staff:
            queryset = queryset.filter(user=user)
        else:
            user_id = self.request.query_params.get("user_id")
            if user_id:
                queryset = queryset.filter(user__id=user_id)

        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            if is_active.lower() == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active.lower() == "false":
                queryset = queryset.exclude(actual_return_date__isnull=True)

        return queryset

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
