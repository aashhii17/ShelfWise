from datetime import timedelta
from django import forms
from django.utils import timezone
from django.db import models
from .models import Book, Loan, Member


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title", "author", "year", "category"]
        widgets = {"year": forms.NumberInput(attrs={"min": 1, "max": 9999})}


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["member_id", "name", "email"]
        labels = {
            "member_id": "Member ID",
            "name": "Full Name",
            "email": "Email Address",
        }


class IssueForm(forms.ModelForm):
    member = forms.ModelChoiceField(queryset=Member.objects.all(), label="Select Library Member")

    class Meta:
        model = Loan
        fields = ["member"]

    def save(self, book, commit=True):
        loan = super().save(commit=False)
        loan.book = book
        loan.borrower_name = self.cleaned_data["member"].name
        loan.borrower_id = self.cleaned_data["member"].member_id
        loan.issued_at = timezone.now()
        loan.due_date = (loan.issued_at + timedelta(days=7)).date()
        if commit:
            loan.save()
        return loan


class GlobalIssueForm(forms.ModelForm):
    book = forms.ModelChoiceField(queryset=Book.objects.none(), label="Select Book to Issue")
    member = forms.ModelChoiceField(queryset=Member.objects.all(), label="Select Library Member")

    class Meta:
        model = Loan
        fields = ["book", "member"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show only available books (no active loans)
        active_loans = Loan.objects.filter(returned_at__isnull=True)
        unavailable_ids = set(active_loans.values_list("book_id", flat=True))
        self.fields["book"].queryset = Book.objects.exclude(id__in=unavailable_ids)



