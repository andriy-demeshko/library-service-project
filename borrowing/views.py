from rest_framework import viewsets, mixins

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingReadSerializer,
    BorrowingCreateSerializer,
)


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.select_related("book", "user")

    # def get_queryset(self):
    #     return Borrowing.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return BorrowingReadSerializer

        elif self.action == "create":
            return BorrowingCreateSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
