from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("books/add/", views.add_book, name="add_book"),
    path("books/<int:pk>/", views.book_detail, name="book_detail"),
    path("books/<int:pk>/issue/", views.issue_book, name="issue_book"),
    path("loans/<int:pk>/extend/", views.extend_loan, name="extend_loan"),
    path("loans/<int:pk>/return/", views.return_book, name="return_book"),
    path("loans/", views.loan_history, name="loan_history"),
    path("doctors/register/", views.register_doctor, name="register_doctor"),
    path("doctors/", views.doctor_list, name="doctor_list"),
    path("appointments/schedule/", views.schedule_appointment, name="schedule_appointment"),
]
