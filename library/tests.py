from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Book, Loan


class LibraryTests(TestCase):
    def setUp(self):
        self.book = Book.objects.create(title="Test Book", author="Test Author", year=2026)

    def test_home_and_search(self):
        response = self.client.get(reverse("home"), {"q": "Test Author"})
        self.assertContains(response, "Test Book")

    def test_add_book(self):
        self.client.post(reverse("add_book"), {"title": "New Book", "author": "Writer", "year": 2020})
        self.assertTrue(Book.objects.filter(title="New Book").exists())

    def test_issue_and_return_book(self):
        response = self.client.post(reverse("issue_book", args=[self.book.pk]), {"borrower_name": "Sandeep", "borrower_id": "ST01"})
        self.assertRedirects(response, reverse("book_detail", args=[self.book.pk]))
        loan = Loan.objects.get(book=self.book)
        self.assertEqual(loan.due_date, timezone.localdate() + timedelta(days=7))
        self.client.post(reverse("return_book", args=[loan.pk]))
        loan.refresh_from_db()
        self.assertIsNotNone(loan.returned_at)

    def test_extend_loan(self):
        loan = Loan.objects.create(
            book=self.book,
            borrower_name="Sandeep",
            borrower_id="ST01",
            issued_at=timezone.now(),
            due_date=timezone.localdate() + timedelta(days=7),
        )
        response = self.client.post(reverse("extend_loan", args=[loan.pk]))
        self.assertRedirects(response, reverse("book_detail", args=[self.book.pk]))
        loan.refresh_from_db()
        self.assertEqual(loan.due_date, timezone.localdate() + timedelta(days=14))

    def test_cannot_issue_unavailable_book(self):
        Loan.objects.create(book=self.book, borrower_name="One", borrower_id="1", due_date=timezone.localdate())
        self.client.post(reverse("issue_book", args=[self.book.pk]), {"borrower_name": "Two", "borrower_id": "2"})
        self.assertEqual(Loan.objects.filter(book=self.book).count(), 1)


