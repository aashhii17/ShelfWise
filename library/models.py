from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Member(models.Model):
    member_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True, null=True)
    joined_at = models.DateField(default=timezone.localdate)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.member_id})"


class Book(models.Model):
    CATEGORY_CHOICES = [
        ("Python", "Python"),
        ("Java", "Java"),
        ("C++", "C++"),
        ("Data Science", "Data Science"),
        ("General", "General"),
    ]
    title = models.CharField(max_length=250, unique=True)
    author = models.CharField(max_length=250)
    year = models.PositiveIntegerField(blank=True, null=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default="General")

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
        if last_loan:
            return last_loan.member.name if last_loan.member else last_loan.borrower_name
        return None


class Loan(models.Model):
    book = models.ForeignKey(Book, related_name="loans", on_delete=models.PROTECT)
    member = models.ForeignKey(Member, related_name="loans", on_delete=models.PROTECT, null=True, blank=True)
    borrower_name = models.CharField(max_length=120, blank=True, null=True)
    borrower_id = models.CharField(max_length=50, blank=True, null=True)
    issued_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateField()
    returned_at = models.DateTimeField(blank=True, null=True)
    fine_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    fine_paid = models.BooleanField(default=False)

    class Meta:
        ordering = ["-issued_at"]

    def save(self, *args, **kwargs):
        if not self.due_date:
            # Set default 7 days from now
            self.due_date = (self.issued_at + timedelta(days=7)).date()
        
        # Calculate fine if overdue and not paid yet
        if self.is_overdue:
            overdue_days = (timezone.localdate() - self.due_date).days
            self.fine_amount = max(0.00, overdue_days * 1.00)  # $1 per day
        elif self.returned_at and self.returned_at.date() > self.due_date:
            overdue_days = (self.returned_at.date() - self.due_date).days
            self.fine_amount = max(0.00, overdue_days * 1.00)

        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        return self.returned_at is None and self.due_date < timezone.localdate()

    def __str__(self):
        borrower = self.member.name if self.member else self.borrower_name
        return f"{self.book} — {borrower}"

    @property
    def is_active(self):
        return self.returned_at is None

    @property
    def overdue_days(self):
        if self.returned_at:
            if self.returned_at.date() > self.due_date:
                return (self.returned_at.date() - self.due_date).days
            return 0
        if self.due_date >= timezone.localdate():
            return 0
        return (timezone.localdate() - self.due_date).days

    @property
    def status(self):
        if self.returned_at:
            return "Returned"
        if self.is_overdue:
            return "Overdue"
        return "Due"



