import stripe
from django.http import HttpRequest
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from stripe.checkout import Session

from LibraryService.settings import STRIPE_SECRET_KEY
from payment_app.models import Payment
from payment_app.serializers import PaymentSerializer, PaymentListSerializer

stripe.api_key = STRIPE_SECRET_KEY


class PaymentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Payment.objects.select_related("borrowing")
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset

        return self.queryset.filter(borrowing__user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer

        return self.serializer_class

    @staticmethod
    def create_stripe_session(
        payment: Payment, request: HttpRequest
    ) -> Session | Response:
        if payment.status != Payment.Status.PENDING:
            return Response(
                {"detail": "Payment already processed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": payment.borrowing.book.title,
                            },
                            "unit_amount": int(payment.money_to_pay * 100),
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=request.build_absolute_uri(
                    reverse(
                        "payment_app:payment-detail", kwargs={"pk": payment.pk}
                    )
                ),
                cancel_url=request.build_absolute_uri(
                    reverse("borrowing_app:borrowing-list")
                ),
            )

            payment.session_id = session.id
            payment.session_url = session.url
            payment.save()

            return session

        except Exception as e:

            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
