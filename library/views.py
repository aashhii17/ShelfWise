from datetime import timedelta

from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import BookForm, IssueForm
from .models import Book, Loan


def home(request):
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "all").strip().lower()
    
    books = Book.objects.prefetch_related("loans").annotate(
        active_loan_count=Count("loans", filter=Q(loans__returned_at__isnull=True)),
        total_loan_count=Count("loans"),
    )
    
    if query:
        books = books.filter(
            Q(title__icontains=query)
            | Q(author__icontains=query)
            | Q(loans__borrower_name__icontains=query)
            | Q(loans__borrower_id__icontains=query)
        ).distinct()
        
    active_loans = Loan.objects.filter(returned_at__isnull=True).select_related("book")
    unavailable_ids = set(active_loans.values_list("book_id", flat=True))
    overdue_count = active_loans.filter(due_date__lt=timezone.localdate()).count()
    
    if status_filter == "available":
        books = books.filter(active_loan_count=0)
    elif status_filter == "loaned":
        books = books.filter(active_loan_count__gt=0)
    elif status_filter == "overdue":
        books = books.filter(loans__returned_at__isnull=True, loans__due_date__lt=timezone.localdate()).distinct()
        
    popular_books = (
        Book.objects.annotate(total_loan_count=Count("loans"))
        .order_by("-total_loan_count", "title")[:4]
    )
    
    return render(request, "library/home.html", {
        "books": books,
        "query": query,
        "status_filter": status_filter,
        "unavailable_ids": unavailable_ids,
        "book_count": Book.objects.count(),
        "available_count": Book.objects.count() - len(unavailable_ids),
        "active_loans": active_loans,
        "overdue_count": overdue_count,
        "popular_books": popular_books,
    })


def loan_history(request):
    status_filter = request.GET.get("status", "all").strip().lower()
    query = request.GET.get("q", "").strip()
    
    loans = Loan.objects.select_related("book").order_by("-issued_at")
    
    if query:
        loans = loans.filter(
            Q(book__title__icontains=query) |
            Q(borrower_name__icontains=query) |
            Q(borrower_id__icontains=query)
        )
        
    if status_filter == "active":
        loans = loans.filter(returned_at__isnull=True)
    elif status_filter == "returned":
        loans = loans.filter(returned_at__isnull=False)
    elif status_filter == "overdue":
        loans = loans.filter(returned_at__isnull=True, due_date__lt=timezone.localdate())
        
    return render(request, "library/loan_list.html", {
        "loans": loans,
        "status_filter": status_filter,
        "query": query,
    })


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    current_loan = book.current_loan
    history = book.loans.select_related("book").order_by("-issued_at")[:8]
    return render(request, "library/book_detail.html", {
        "book": book,
        "current_loan": current_loan,
        "history": history,
    })


def add_book(request):
    form = BookForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        book = form.save()
        messages.success(request, f'“{book.title}” was added to the library.')
        return redirect("book_detail", pk=book.pk)
    return render(request, "library/form.html", {"form": form, "title": "Add a new book", "button": "Add book"})


@transaction.atomic
def issue_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if Loan.objects.select_for_update().filter(book=book, returned_at__isnull=True).exists():
        messages.error(request, "That book is currently issued to another member.")
        return redirect("book_detail", pk=book.pk)
    form = IssueForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        loan = form.save(book)
        messages.success(request, f'“{book.title}” issued successfully. Due {loan.due_date:%d %b %Y}.')
        return redirect("book_detail", pk=book.pk)
    return render(request, "library/form.html", {"form": form, "title": f"Issue {book.title}", "button": "Confirm issue", "book": book})


def extend_loan(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    loan = get_object_or_404(Loan, pk=pk, returned_at__isnull=True)
    if loan.is_overdue:
        messages.error(request, "Overdue loans cannot be extended. Please return the book first.")
    else:
        loan.due_date += timedelta(days=7)
        loan.save(update_fields=["due_date"])
        messages.success(request, f'Loan for “{loan.book.title}” was extended to {loan.due_date:%d %b %Y}.')
    return redirect("book_detail", pk=loan.book.pk)


def return_book(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    loan = get_object_or_404(Loan, pk=pk, returned_at__isnull=True)
    loan.returned_at = timezone.now()
    loan.save(update_fields=["returned_at"])
    messages.success(request, f'“{loan.book.title}” has been returned.')
    if loan.book_id:
        return redirect("book_detail", pk=loan.book.pk)
    return redirect("home")



