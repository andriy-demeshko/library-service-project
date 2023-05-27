from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from books.models import Book
from books.serializers import (
    BookListSerializer,
    BookSerializer,
)

BOOKS_URL = reverse("books:book-list")


def sample_book(**params):
    defaults = {
        "title": "Test book",
        "author": "Test author",
        "cover": "SOFT",
        "inventory": 2,
        "daily_fee": 4,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def detail_url(book_id):
    return reverse("books:book-detail", args=[book_id])


class UnauthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_book(self):
        sample_book()
        sample_book()

        res = self.client.get(BOOKS_URL)

        books = Book.objects.order_by("id")
        serializer = BookListSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_book_detail(self):
        book = sample_book()

        url = detail_url(book.id)
        res = self.client.get(url)

        serializer = BookSerializer(book)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_auth_required(self):
        book = sample_book()
        url = detail_url(book.id)

        res_post = self.client.post(BOOKS_URL)
        self.assertEqual(res_post.status_code, status.HTTP_401_UNAUTHORIZED)

        res_post = self.client.put(url)
        self.assertEqual(res_post.status_code, status.HTTP_401_UNAUTHORIZED)

        res_del = self.client.delete(url)
        self.assertEqual(res_del.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@test.com",
            "user_password",
        )
        self.client.force_authenticate(self.user)

    def test_list_book(self):
        sample_book()
        sample_book()

        res = self.client.get(BOOKS_URL)

        books = Book.objects.order_by("id")
        serializer = BookListSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_book_detail(self):
        book = sample_book()

        url = detail_url(book.id)
        res = self.client.get(url)

        serializer = BookSerializer(book)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_admin_required(self):
        book = sample_book()
        url = detail_url(book.id)

        res_post = self.client.post(BOOKS_URL)
        self.assertEqual(res_post.status_code, status.HTTP_403_FORBIDDEN)

        res_post = self.client.put(url)
        self.assertEqual(res_post.status_code, status.HTTP_403_FORBIDDEN)

        res_del = self.client.delete(url)
        self.assertEqual(res_del.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@test.com",
            "admin_password",
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        payload = {
            "title": "Super book",
            "author": "Super author",
            "cover": "HARD",
            "inventory": 4,
            "daily_fee": 1,
        }

        res = self.client.post(BOOKS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        book = Book.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(book, key))

    def test_put_book(self):
        payload = {
            "title": "Super book",
            "author": "Super author",
            "cover": "HARD",
            "inventory": 4,
            "daily_fee": 1,
        }

        book = sample_book()
        url = detail_url(book.id)

        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        book.refresh_from_db()
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(book, key))

    def test_patch_book(self):
        payload = {
            "cover": "HARD",
            "inventory": 8,
            "daily_fee": 2,
        }

        book = sample_book()
        url = detail_url(book.id)

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        book.refresh_from_db()
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(book, key))

    def test_delete_book(self):
        book = sample_book()
        url = detail_url(book.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=book.id).exists())
