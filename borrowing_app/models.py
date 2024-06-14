from django.db import models

from user.models import User
from books_app.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField()
    books = models.ManyToManyField(Book, related_name='borrowings')
    users = models.ForeignKey(User, on_delete=models.CASCADE, related_name="borrowings")
