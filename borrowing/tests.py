from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from books.models import Book
from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingReadSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)

BORROWING_URL = reverse("borrowing:borrowing-list")


def sample_borrowing(**params):
    book = Book.objects.create(
        title="Test book",
        author="Test author",
        cover="SOFT",
        inventory=2,
        daily_fee=4,
    )

    defaults = {
        "borrow_date": date.today(),
        "expected_return_date": date.today() + timedelta(days=10),
        "actual_return_date": None,
        "book": book,
        "user": None,
    }
    defaults.update(params)

    return Borrowing.objects.create(**defaults)


def detail_url(borrowing_id):
    return reverse("borrowing:borrowing-detail", args=[borrowing_id])


class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@test.com",
            "user_password",
        )
        self.client.force_authenticate(self.user)

    def test_list_only_own_borrowings(self):
        sample_borrowing(user=self.user)
        sample_borrowing(user=self.user)
        sample_borrowing(
            user=get_user_model().objects.create_user(
                "another@test.com",
                "another_password",
            )
        )

        res = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.filter(user=self.user)
        serializer = BorrowingReadSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_borrowing_detail(self):
        borrowing = sample_borrowing(user=self.user)

        url = detail_url(borrowing.id)
        res = self.client.get(url)

        serializer = BorrowingReadSerializer(borrowing)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_borrowing(self):
        self.book = Book.objects.create(
            title="Test book",
            author="Test author",
            cover="SOFT",
            inventory=2,
            daily_fee=4,
        )
        payload = {
            "book": self.book.id,
            "expected_return_date": date.today() + timedelta(days=15),
        }

        res = self.client.post(BORROWING_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        borrowing = Borrowing.objects.get(id=res.data["id"])

        self.assertEqual(borrowing.user, self.user)
        self.assertEqual(borrowing.book.id, self.book.id)
        self.assertEqual(borrowing.book.inventory, self.book.inventory - 1)

    def test_return_borrowing_forbidden(self):
        borrowing = sample_borrowing(user=self.user)
        payload = {
            "actual_return_date": date.today(),
        }
        res = self.client.post(f"/api/borrowings/{borrowing.id}/return/", payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@test.com",
            "admin_password",
        )
        self.client.force_authenticate(self.user)

    def test_list_all_borrowings(self):
        sample_borrowing(user=self.user)
        sample_borrowing(user=self.user)
        sample_borrowing(
            user=get_user_model().objects.create_user(
                "another@test.com",
                "another_password",
            )
        )

        res = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.order_by("id")
        serializer = BorrowingReadSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_borrowings_by_user_id(self):
        user1 = get_user_model().objects.create_user(
            "user1@test.com",
            "user1_password",
        )
        user2 = get_user_model().objects.create_user(
            "user2@test.com",
            "user2_password",
        )

        borrowing1 = sample_borrowing(user=user1)
        borrowing2 = sample_borrowing(user=user2)

        res = self.client.get(BORROWING_URL, {"user_id": user1.id})

        serializer1 = BorrowingReadSerializer(borrowing1)
        serializer2 = BorrowingReadSerializer(borrowing2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_borrowings_by_is_active(self):
        borrowing1 = sample_borrowing(user=self.user)
        borrowing2 = sample_borrowing(user=self.user)
        borrowing3 = sample_borrowing(
            user=self.user,
            actual_return_date=date.today(),
        )

        res = self.client.get(BORROWING_URL, {"is_active": "true"})

        serializer1 = BorrowingReadSerializer(borrowing1)
        serializer2 = BorrowingReadSerializer(borrowing2)
        serializer3 = BorrowingReadSerializer(borrowing3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_return_borrowing(self):
        borrowing = sample_borrowing(user=self.user)

        res = self.client.post(f"/api/borrowings/{borrowing.id}/return/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        borrowing.refresh_from_db()
        self.assertEqual(borrowing.book.inventory, 3)
        self.assertEqual(borrowing.actual_return_date, date.today())

        res = self.client.post(f"/api/borrowings/{borrowing.id}/return/")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            res.data["detail"],
            "Borrowing has already been returned.",
        )
