from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("books/add/", views.add_book, name="add_book"),
    path("books/<int:pk>/", views.book_detail, name="book_detail"),
    path("books/<int:pk>/issue/", views.issue_book, name="issue_book"),
    path("issue/", views.issue_book_global, name="issue_book_global"),
    path("loans/<int:pk>/extend/", views.extend_loan, name="extend_loan"),
    path("loans/<int:pk>/return/", views.return_book, name="return_book"),
    path("loans/<int:pk>/pay-fine/", views.pay_fine, name="pay_fine"),
    path("loans/", views.loan_history, name="loan_history"),
    path("members/", views.members_list, name="members_list"),
    path("members/add/", views.add_member, name="add_member"),
    path("members/<int:pk>/", views.member_detail, name="member_detail"),
    path("fines/", views.fines_list, name="fines_list"),
]
