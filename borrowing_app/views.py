from django.shortcuts import redirect
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from borrowing_app.models import Borrowing
from borrowing_app.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingReturnSerializer,
)
from payment_app.models import Payment
from payment_app.views import PaymentViewSet
from .tasks import send_telegram_message


class BorrowingViewSet(
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet
):
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
        elif self.action == "return_book":
            return BorrowingReturnSerializer
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

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="return",
    )
    def return_book(self, request, pk=None):
        borrowing = self.get_object()
        serializer = BorrowingReturnSerializer(
            borrowing, data=request.data, partial=True
        )
        if borrowing.expiated:
            payment_type = Payment.Type.FINE
            money_to_pay = borrowing.fine_payable
        else:
            payment_type = Payment.Type.PAYMENT
            money_to_pay = borrowing.payable

        payment, created = Payment.objects.get_or_create(
            borrowing_id=borrowing.id,
            defaults={"money_to_pay": money_to_pay, "type": payment_type},
        )

        if serializer.is_valid():
            serializer.save()

            if not created and payment.status == Payment.Status.PAID:
                return Response(
                    {"detail": "Payment already processed"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            checkout_session = PaymentViewSet.create_stripe_session(
                payment, request
            )

            if isinstance(checkout_session, Response):
                return checkout_session

            return redirect(
                checkout_session.url, status=status.HTTP_307_TEMPORARY_REDIRECT
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
