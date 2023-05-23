from rest_framework import viewsets

from borrowing.models import Borrowing
from borrowing.serializers import BorrowingReadSerializer


class BorrowingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingReadSerializer
