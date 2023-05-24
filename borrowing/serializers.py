from django.db import transaction
from rest_framework import serializers

from books.serializers import BookSerializer
from borrowing.models import Borrowing


# class BorrowingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Borrowing
#         fields = (
#             "id",
#             "borrow_date",
#             "expected_return_date",
#             "actual_return_date",
#             "book",
#             "user",
#         )


class BorrowingReadSerializer(serializers.ModelSerializer):
    book = BookSerializer(many=False, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "expected_return_date",
        )

    def validate_book(self, book):
        if book.inventory == 0:
            raise serializers.ValidationError("Book is out of stock.")
        return book

    def create(self, validated_data):
        with transaction.atomic():
            book = validated_data.pop("book")
            book.inventory -= 1
            book.save()

            borrowing = Borrowing.objects.create(book=book, **validated_data)

            return borrowing
