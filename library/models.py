from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Book(models.Model):
    title = models.CharField(max_length=250, unique=True)
    author = models.CharField(max_length=250)
    year = models.PositiveIntegerField(blank=True, null=True)

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
        return last_loan.borrower_name if last_loan else None


class Loan(models.Model):
    book = models.ForeignKey(Book, related_name="loans", on_delete=models.PROTECT)
    borrower_name = models.CharField(max_length=120)
    borrower_id = models.CharField(max_length=50)
    issued_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateField()
    returned_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-issued_at"]

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = (self.issued_at + timedelta(days=7)).date()
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        return self.returned_at is None and self.due_date < timezone.localdate()

    def __str__(self):
        return f"{self.book} — {self.borrower_name}"

    @property
    def is_active(self):
        return self.returned_at is None

    @property
    def overdue_days(self):
        if self.returned_at or self.due_date >= timezone.localdate():
            return 0
        return (timezone.localdate() - self.due_date).days

    @property
    def status(self):
        if self.returned_at:
            return "Returned"
        if self.is_overdue:
            return "Overdue"
        return "Due"


class Doctor(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    speciality = models.CharField(max_length=200)
    ehic_number = models.CharField(max_length=20, unique=True)
    identity_proof = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    verified = models.BooleanField(default=False)
    registered_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.full_name()} — {self.speciality}"

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def verify_ehic(self):
        ehic = self.ehic_number.replace(" ", "")
        if len(ehic) == 12 and ehic[:2].isalpha() and ehic[2:].isdigit() and self.identity_proof:
            return True
        return False

    def save(self, *args, **kwargs):
        self.verified = self.verify_ehic()
        super().save(*args, **kwargs)

    @property
    def upcoming_appointments(self):
        return self.appointments.filter(status__in=[Appointment.STATUS_REQUESTED, Appointment.STATUS_CONFIRMED], appointment_datetime__gte=timezone.now()).order_by("appointment_datetime")


class Appointment(models.Model):
    STATUS_REQUESTED = "requested"
    STATUS_CONFIRMED = "confirmed"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_REQUESTED, "Requested"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    doctor = models.ForeignKey(Doctor, related_name="appointments", on_delete=models.PROTECT)
    patient_name = models.CharField(max_length=150)
    patient_email = models.EmailField(blank=True)
    patient_phone = models.CharField(max_length=20, blank=True)
    appointment_datetime = models.DateTimeField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_REQUESTED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["appointment_datetime"]
        unique_together = [["doctor", "appointment_datetime"]]

    def __str__(self):
        return f"{self.patient_name} with {self.doctor.full_name()} at {self.appointment_datetime:%Y-%m-%d %H:%M}"

    def clean(self):
        now = timezone.now()
        if self.appointment_datetime < now + timedelta(hours=24):
            raise ValidationError({"appointment_datetime": "Appointments must be booked at least 24 hours in advance."})

        appointment_hour = self.appointment_datetime.hour
        if appointment_hour < 9 or appointment_hour >= 17:
            raise ValidationError({"appointment_datetime": "Appointments are available only between 09:00 and 17:00."})

        if not self.doctor.verified:
            raise ValidationError({"doctor": "Only verified doctors can receive appointments."})

        overlap_start = self.appointment_datetime - timedelta(minutes=29)
        overlap_end = self.appointment_datetime + timedelta(minutes=29)
        conflicts = Appointment.objects.filter(
            doctor=self.doctor,
            status__in=[self.STATUS_REQUESTED, self.STATUS_CONFIRMED],
            appointment_datetime__range=(overlap_start, overlap_end),
        )
        if self.pk:
            conflicts = conflicts.exclude(pk=self.pk)
        if conflicts.exists():
            raise ValidationError({"appointment_datetime": "This doctor already has an appointment at or near this time."})

    @property
    def is_upcoming(self):
        return self.appointment_datetime >= timezone.now() and self.status in [self.STATUS_REQUESTED, self.STATUS_CONFIRMED]
