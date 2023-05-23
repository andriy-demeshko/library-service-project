from django.db import models

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date, timedelta

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField(
        validators=[
            MinValueValidator(limit_value=date.today() + timedelta(days=1)),
            MaxValueValidator(limit_value=date.today() + timedelta(days=30)),
        ]
    )
    actual_return_date = models.DateField(default=None, null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings"
    )
