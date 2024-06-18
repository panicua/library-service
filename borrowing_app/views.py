from django.shortcuts import redirect
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema_view,
    OpenApiParameter,
    extend_schema,
    OpenApiExample,
)
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


@extend_schema_view(
    list=extend_schema(
        summary="Retrieve a list of borrowings",
        description="Retrieve a list of all books. Accessible by authenticated user.",
        parameters=[
            OpenApiParameter(
                name="is_active",
                description=(
                    "Filter borrowing list by actual return date"
                    "(ex. ?is_active=true)"
                ),
                required=False,
                type=OpenApiTypes.BOOL,
            ),
            OpenApiParameter(
                name="user_id",
                description=(
                    "Filter borrowing list by user id, only for admins"
                    "(ex. ?user_id=5)"
                ),
                required=False,
                type=OpenApiTypes.INT,
            ),
        ],
        responses={200: BorrowingListSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Borrowing list example",
                value={
                    "id": 1,
                    "borrow_date": "2024-06-18",
                    "expected_return_date": "2024-06-18",
                    "actual_return_date": "2024-06-18",
                    "book": {
                        "id": 1,
                        "title": "Kobzar",
                        "author": "Taras Shevchenko",
                        "cover": "HARD",
                        "inventory": 120,
                        "daily_fee": "4",
                    },
                    "user": {
                        "id": 1,
                        "email": "user@example.com",
                        "is_staff": True,
                    },
                    "payment": {
                        "id": 1,
                        "status": "PENDING",
                        "type": "PAYMENT",
                        "session_url": "string",
                        "session_id": "string",
                        "money_to_pay": "4",
                        "borrowing": 1,
                    },
                },
            )
        ],
    ),
    retrieve=extend_schema(
        summary="Retrieve a single borrowing",
        description="Retrieve the details of a specific borrowing by its ID. Accessible by authenticated user.",
        responses={200: BorrowingListSerializer}
    ),
    create=extend_schema(
        summary="Create a new borrowing",
        description="Create a new book. Accessible by authenticated user.",
        responses={201: BorrowingSerializer}
    ),
)
class BorrowingViewSet(
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet
):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.select_related("user", "book")
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

    @extend_schema(
        summary="Return a borrowed book",
        description="Mark a book as returned and process the payment for the borrowing.",
        request=BorrowingReturnSerializer,
        responses={200: BorrowingReturnSerializer},
        examples=[
            OpenApiExample("Request body example", value={}),
            OpenApiExample(
                "Return book example",
                value={
                    "id": 1,
                    "actual_return_date": "2024-06-18",
                    "payment": {
                        "id": 1,
                        "status": "PAID",
                        "type": "PAYMENT",
                        "session_url": "string",
                        "session_id": "string",
                        "money_to_pay": "4",
                        "borrowing": 1,
                    },
                },
            ),
        ],
    )
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
