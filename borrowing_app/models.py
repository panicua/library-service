from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models

from LibraryService.settings import FINE_COEFFICIENT
from books_app.models import Book

User = get_user_model()


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="borrowings"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="borrowings"
    )

    class Meta:
        verbose_name = "borrowing"
        verbose_name_plural = "borrowings"

    def __str__(self):
        return f"Book taken {self.borrow_date} to borrow {self.expected_return_date}"

    @property
    def payable(self):
        days_borrowed = (date.today() - self.borrow_date).days + 1
        daily_fee = Decimal(self.book.daily_fee)
        return Decimal(days_borrowed) * daily_fee

    @property
    def fine_payable(self):
        return Decimal((
            (self.overdue_days + self.borrow_days) + 1
            * Decimal(self.book.daily_fee)
        ) * FINE_COEFFICIENT)

    @property
    def expiated(self) -> bool:
        if not self.actual_return_date:
            self.actual_return_date = date.today()
        return self.expected_return_date < self.actual_return_date

    @property
    def overdue_days(self) -> int:
        return (self.actual_return_date - self.expected_return_date).days

    @property
    def borrow_days(self) -> int:
        return (self.expected_return_date - self.borrow_date).days
