from django.contrib import admin

from .models import Appointment, Book, Doctor, Loan


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "year"]
    search_fields = ["title", "author"]


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ["book", "borrower_name", "borrower_id", "issued_at", "due_date", "returned_at"]
    list_filter = ["returned_at", "due_date"]
    search_fields = ["book__title", "borrower_name", "borrower_id"]


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ["full_name", "speciality", "ehic_number", "verified", "registered_at"]
    search_fields = ["first_name", "last_name", "speciality", "ehic_number"]
    list_filter = ["verified", "speciality"]


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ["doctor", "patient_name", "appointment_datetime", "status"]
    list_filter = ["status", "appointment_datetime", "doctor"]
    search_fields = ["patient_name", "patient_email", "doctor__first_name", "doctor__last_name"]
