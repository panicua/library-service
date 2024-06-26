from django.urls import path, include
from rest_framework import routers

from payment_app.views import PaymentViewSet

router = routers.DefaultRouter()

router.register("", PaymentViewSet, basename="payment")

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "payment_app"
