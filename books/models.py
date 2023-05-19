from django.db import models
from django.core.validators import MinValueValidator


class Book(models.Model):
    COVER_CHOICES = [
        ("HARD", "Hardcover"),
        ("SOFT", "Softcover"),
    ]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=4, choices=COVER_CHOICES)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.00)],
    )

    def __str__(self):
        return self.title

    def borrowing_book(self):
        if self.inventory > 0:
            self.inventory -= 1
            self.save()
        else:
            return "This book is not available"
