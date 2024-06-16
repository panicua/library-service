import stripe
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse

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

        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer

        return self.serializer_class

    @action(detail=True, methods=["post"])
    def create_stripe_session(self, request, pk=None):
        payment = self.get_object()
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
            return Response(
                {"session_url": session.url}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
