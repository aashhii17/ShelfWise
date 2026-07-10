from django.contrib import admin

from .models import Book, Loan


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "year"]
    search_fields = ["title", "author"]


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ["book", "borrower_name", "borrower_id", "issued_at", "due_date", "returned_at"]
    list_filter = ["returned_at", "due_date"]
    search_fields = ["book__title", "borrower_name", "borrower_id"]
