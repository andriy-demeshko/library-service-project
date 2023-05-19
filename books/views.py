from rest_framework import viewsets
from rest_framework.response import Response

from books.models import Book
from books.serializers import (
    BookSerializer,
    BookListSerializer,
)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def borrowing_book(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.inventory > 0:
            instance.inventory -= 1
            instance.save()
            return Response({"message": "Book borrowed successfully."})
        else:
            return Response({"message": "This book is not available."})

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer

        return self.serializer_class
