from datetime import timedelta

from django import forms
from django.utils import timezone

from .models import Appointment, Book, Doctor, Loan


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


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = [
            "first_name",
            "last_name",
            "speciality",
            "ehic_number",
            "identity_proof",
            "contact_email",
            "contact_phone",
        ]
        labels = {
            "ehic_number": "EHIC number",
            "identity_proof": "Identity proof details",
            "contact_phone": "Phone number",
        }

    def clean_identity_proof(self):
        proof = self.cleaned_data.get("identity_proof", "").strip()
        if not proof:
            raise forms.ValidationError("Please provide identity proof details to confirm your medical registration.")
        return proof

    def clean_ehic_number(self):
        ehic = self.cleaned_data.get("ehic_number", "").strip()
        cleaned = ehic.replace(" ", "")
        if len(cleaned) != 12 or not cleaned[:2].isalpha() or not cleaned[2:].isdigit():
            raise forms.ValidationError("Enter a valid 12-character EHIC number beginning with two letters.")
        return ehic


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            "doctor",
            "patient_name",
            "patient_email",
            "patient_phone",
            "appointment_datetime",
            "reason",
        ]
        widgets = {
            "appointment_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "reason": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_appointment_datetime(self):
        appointment_datetime = self.cleaned_data.get("appointment_datetime")
        if appointment_datetime and appointment_datetime < timezone.now() + timedelta(hours=24):
            raise forms.ValidationError("Appointments must be requested at least 24 hours in advance.")
        return appointment_datetime

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get("doctor")
        if doctor and not doctor.verified:
            raise forms.ValidationError("Please select a verified doctor for real-world appointments.")
        return cleaned_data
