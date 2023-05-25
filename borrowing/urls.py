from django.urls import path, include
from rest_framework import routers

from borrowing.views import BorrowingViewSet

router = routers.DefaultRouter()
router.register("", BorrowingViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "<int:pk>/return/",
        BorrowingViewSet.as_view({"post": "return_borrowing"}),
        name="return-borrowing",
    ),
]

app_name = "borrowing"
