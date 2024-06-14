from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from borrowing_app.models import Borrowing


class Payment(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"

    class Type(models.TextChoices):
        PAYMENT = "PAYMENT", "Payment"
        FINE = "FINE", "Fine"

    status = models.CharField(
        max_length=7,
        choices=Status.choices,
        default=Status.PENDING
    )
    type = models.CharField(
        max_length=7,
        choices=Type.choices,
        default=Type.PAYMENT
    )

    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="payments"
    )

    session_url = models.URLField(max_length=255)
    session_id = models.IntegerField(max_length=63)

    money_to_pay = models.DecimalField(max_digits=10,
                                       decimal_places=2,
                                       validators=[MinValueValidator(Decimal('0.0'))])

    def __str__(self):
        return f"Payment: {self.id}; Pay: {self.money_to_pay};"
