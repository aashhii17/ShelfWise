from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Appointment, Book, Doctor, Loan


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

    def test_doctor_registration_and_verification(self):
        response = self.client.post(reverse("register_doctor"), {
            "first_name": "Jane",
            "last_name": "Doe",
            "speciality": "Cardiology",
            "ehic_number": "AB1234567890",
            "identity_proof": "Medical Council registration 12345",
            "contact_email": "jane.doe@example.com",
            "contact_phone": "1234567890",
        })
        self.assertRedirects(response, reverse("home"))
        doctor = Doctor.objects.get(first_name="Jane", last_name="Doe")
        self.assertTrue(doctor.verified)

    def test_schedule_appointment_for_verified_doctor(self):
        doctor = Doctor.objects.create(
            first_name="Jane",
            last_name="Doe",
            speciality="Cardiology",
            ehic_number="AB1234567890",
            identity_proof="Registration 12345",
        )
        self.assertTrue(doctor.verified)
        appointment_time = (timezone.now() + timedelta(days=2)).replace(hour=10, minute=0, second=0, microsecond=0)
        response = self.client.post(reverse("schedule_appointment"), {
            "doctor": doctor.pk,
            "patient_name": "John Smith",
            "patient_email": "john.smith@example.com",
            "patient_phone": "5551234567",
            "appointment_datetime": appointment_time.strftime("%Y-%m-%dT%H:%M"),
            "reason": "Routine checkup",
        })
        self.assertRedirects(response, reverse("home"))
        self.assertTrue(Appointment.objects.filter(doctor=doctor, patient_name="John Smith").exists())
