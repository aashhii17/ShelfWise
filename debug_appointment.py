import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_site.settings')
django.setup()
from django.test import Client
from django.utils import timezone
from library.models import Doctor

c = Client()
doctor = Doctor.objects.create(
    first_name='Jane',
    last_name='Doe',
    speciality='Cardiology',
    ehic_number='AB1234567890',
    identity_proof='Registration 12345',
)
print('doctor verified', doctor.verified)
appointment_time = timezone.localtime() + timedelta(days=2)
appointment_time = appointment_time.replace(hour=10, minute=0, second=0, microsecond=0)
print('appointment_time', appointment_time)
resp = c.post('/appointments/schedule/', {
    'doctor': doctor.pk,
    'patient_name': 'John Smith',
    'patient_email': 'john.smith@example.com',
    'patient_phone': '5551234567',
    'appointment_datetime': appointment_time.strftime('%Y-%m-%dT%H:%M'),
    'reason': 'Routine checkup',
})
print('status', resp.status_code)
print('redirect chain', resp.redirect_chain)
print('templates', [t.name for t in resp.templates])
form = resp.context.get('form') if resp.context else None
print('form errors', form.errors if form else None)
print('non field errors', form.non_field_errors() if form else None)
