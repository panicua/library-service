from django.db import models

from user.models import User
from books_app.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    books = models.ManyToManyField(Book, related_name='borrowings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="borrowings")

    class Meta:
        verbose_name = 'borrowing'
        verbose_name_plural = 'borrowings'

    def __str__(self):
        return f"Book taken {self.borrow_date} to borrow {self.expected_return_date}"
