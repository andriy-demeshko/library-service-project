from rest_framework import viewsets

from borrowing.models import Borrowing
from borrowing.serializers import BorrowingReadSerializer


class BorrowingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingReadSerializer
