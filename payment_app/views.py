import stripe
from django.http import HttpRequest
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from stripe.checkout import Session

from LibraryService.settings import STRIPE_SECRET_KEY
from borrowing_app.tasks import send_telegram_message
from payment_app.models import Payment
from payment_app.serializers import PaymentSerializer, PaymentListSerializer
from borrowing_app.tasks import send_telegram_message

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

    @action(
        detail=True, methods=["get"], url_path="success", url_name="success"
    )
    def success_payment(self, request, pk=None):
        payment = self.get_object()
        session = stripe.checkout.Session.retrieve(payment.session_id)

        if session.payment_status == "paid":
            payment.status = Payment.Status.PAID
            payment.save()

            send_telegram_message.delay(
                f"*Successful payment!*\n"
                f"*Book title*: {payment.borrowing.book.title},\n"
                f"*User*: {payment.borrowing.user.email},\n"
                f"*Payment id*: {payment.id},\n"
                f"*Money paid*: {payment.money_to_pay},\n"
                f"*Payment status*: {payment.status}"
            )
            return Response({"detail": "Payment was successful!"})

        return Response(
            {"detail": "Payment not completed yet."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=["get"], url_path="cancel", url_name="cancel")
    def cancel_payment(self, request, pk=None):
        payment = self.get_object()
        return Response(
            {
                "detail": f"Payment can be completed within 24 hours "
                          f"using this url {payment.session_url}"
            }
        )

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
                        "payment_app:payment-success",
                        kwargs={"pk": payment.pk},
                    )
                ),
                cancel_url=request.build_absolute_uri(
                    reverse(
                        "payment_app:payment-cancel", kwargs={"pk": payment.pk}
                    )
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
