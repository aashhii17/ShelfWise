from datetime import timedelta
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import BookForm, IssueForm, MemberForm, GlobalIssueForm
from .models import Book, Loan, Member


def home(request):
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "all").strip().lower()
    category_filter = request.GET.get("category", "all").strip()
    
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
        
    if category_filter != "all" and category_filter:
        books = books.filter(category=category_filter)

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

    # Calculate total unpaid fines
    unpaid_fines = Loan.objects.filter(fine_amount__gt=0, fine_paid=False).aggregate(total=Sum("fine_amount"))["total"] or 0.00
    
    categories = [choice[0] for choice in Book.CATEGORY_CHOICES]

    return render(request, "library/home.html", {
        "books": books,
        "query": query,
        "status_filter": status_filter,
        "category_filter": category_filter,
        "categories": categories,
        "unavailable_ids": unavailable_ids,
        "book_count": Book.objects.count(),
        "available_count": Book.objects.count() - len(unavailable_ids),
        "active_loans": active_loans,
        "overdue_count": overdue_count,
        "popular_books": popular_books,
        "unpaid_fines": unpaid_fines,
    })


def loan_history(request):
    status_filter = request.GET.get("status", "all").strip().lower()
    query = request.GET.get("q", "").strip()
    
    loans = Loan.objects.select_related("book", "member").order_by("-issued_at")
    
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
    if not book.is_available:
        messages.error(request, "That book is currently issued to another member.")
        return redirect("book_detail", pk=book.pk)
    
    # Check if there are any members first
    if not Member.objects.exists():
        messages.warning(request, "Please add at least one library member before issuing books.")
        return redirect("add_member")

    form = IssueForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        loan = form.save(book)
        messages.success(request, f'“{book.title}” issued successfully. Due {loan.due_date:%d %b %Y}.')
        return redirect("book_detail", pk=book.pk)
    return render(request, "library/form.html", {"form": form, "title": f"Issue {book.title}", "button": "Confirm issue", "book": book})


@transaction.atomic
def issue_book_global(request):
    if not Member.objects.exists():
        messages.warning(request, "Please add at least one library member before issuing books.")
        return redirect("add_member")

    form = GlobalIssueForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        loan = form.save()
        messages.success(request, f'“{loan.book.title}” issued to {loan.borrower_name} successfully.')
        return redirect("book_detail", pk=loan.book.pk)
    return render(request, "library/form.html", {"form": form, "title": "Issue a Book", "button": "Confirm issue"})


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
    
    # Save calls fine calculation logic in models.py
    loan.save()
    
    if loan.fine_amount > 0:
        messages.warning(request, f'“{loan.book.title}” returned. Overdue fine generated: ${loan.fine_amount:.2f}.')
    else:
        messages.success(request, f'“{loan.book.title}” has been returned.')
    
    return redirect("book_detail", pk=loan.book.pk)


def members_list(request):
    query = request.GET.get("q", "").strip()
    members = Member.objects.annotate(
        active_loans_count=Count("loans", filter=Q(loans__returned_at__isnull=True))
    )
    if query:
        members = members.filter(Q(name__icontains=query) | Q(member_id__icontains=query))
    return render(request, "library/member_list.html", {"members": members, "query": query})


def add_member(request):
    form = MemberForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        member = form.save()
        messages.success(request, f'Member “{member.name}” has been registered.')
        return redirect("member_detail", pk=member.pk)
    return render(request, "library/form.html", {"form": form, "title": "Register a new Member", "button": "Register Member"})


def member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)
    active_loans = member.loans.filter(returned_at__isnull=True).select_related("book")
    loan_history = member.loans.filter(returned_at__isnull=False).select_related("book")
    
    # Calculate outstanding fines
    unpaid_loans = member.loans.filter(fine_amount__gt=0, fine_paid=False)
    total_fines = unpaid_loans.aggregate(total=Sum("fine_amount"))["total"] or 0.00
    
    return render(request, "library/member_detail.html", {
        "member": member,
        "active_loans": active_loans,
        "loan_history": loan_history,
        "total_fines": total_fines,
        "unpaid_loans": unpaid_loans,
    })


def fines_list(request):
    loans_with_fines = Loan.objects.filter(fine_amount__gt=0).select_related("book", "member")
    total_unpaid = loans_with_fines.filter(fine_paid=False).aggregate(total=Sum("fine_amount"))["total"] or 0.00
    return render(request, "library/fines_list.html", {
        "loans": loans_with_fines,
        "total_unpaid": total_unpaid,
    })


def pay_fine(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    loan = get_object_or_404(Loan, pk=pk)
    loan.fine_paid = True
    loan.save(update_fields=["fine_paid"])
    messages.success(request, f"Fine for “{loan.book.title}” successfully marked as paid.")
    return redirect("member_detail", pk=loan.member.pk) if loan.member else redirect("fines_list")



