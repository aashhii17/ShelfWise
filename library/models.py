from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Book(models.Model):
    title = models.CharField(max_length=250, unique=True)
    author = models.CharField(max_length=250)
    year = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    @property
    def is_available(self):
        return not self.loans.filter(returned_at__isnull=True).exists()

    @property
    def current_loan(self):
        return self.loans.filter(returned_at__isnull=True).first()

    @property
    def last_borrower(self):
        last_loan = self.loans.order_by("-issued_at").first()
        return last_loan.borrower_name if last_loan else None


class Loan(models.Model):
    book = models.ForeignKey(Book, related_name="loans", on_delete=models.PROTECT)
    borrower_name = models.CharField(max_length=120)
    borrower_id = models.CharField(max_length=50)
    issued_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateField()
    returned_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-issued_at"]

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = (self.issued_at + timedelta(days=7)).date()
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        return self.returned_at is None and self.due_date < timezone.localdate()

    def __str__(self):
        return f"{self.book} — {self.borrower_name}"

    @property
    def is_active(self):
        return self.returned_at is None

    @property
    def overdue_days(self):
        if self.returned_at or self.due_date >= timezone.localdate():
            return 0
        return (timezone.localdate() - self.due_date).days

    @property
    def status(self):
        if self.returned_at:
            return "Returned"
        if self.is_overdue:
            return "Overdue"
        return "Due"



