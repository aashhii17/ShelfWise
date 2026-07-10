from datetime import timedelta

from django import forms
from django.utils import timezone

from .models import Book, Loan


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title", "author", "year"]
        widgets = {"year": forms.NumberInput(attrs={"min": 1, "max": 9999})}


class IssueForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ["borrower_name", "borrower_id"]
        labels = {"borrower_name": "Your name", "borrower_id": "Student / member ID"}

    def save(self, book, commit=True):
        loan = super().save(commit=False)
        loan.book = book
        loan.issued_at = timezone.now()
        loan.due_date = (loan.issued_at + timedelta(days=7)).date()
        if commit:
            loan.save()
        return loan



