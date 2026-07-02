import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_site.settings')
django.setup()
from django.test import Client
from django.utils import timezone
from library.models import Doctor

client = Client()
doctor = Doctor.objects.create(
    first_name='Jane',
    last_name='Doe',
    speciality='Cardiology',
    ehic_number='EF1234567890',
    identity_proof='Registration 12345',
)
print('verified', doctor.verified)
appointment_time = timezone.now() + timedelta(days=2)
print('timezone.now', timezone.now())
print('appointment_time', appointment_time)
resp = client.post('/appointments/schedule/', {
    'doctor': doctor.pk,
    'patient_name': 'John Smith',
    'patient_email': 'john.smith@example.com',
    'patient_phone': '5551234567',
    'appointment_datetime': appointment_time.strftime('%Y-%m-%dT%H:%M'),
    'reason': 'Routine checkup',
})
print('status', resp.status_code)
print('redirect chain', getattr(resp, 'redirect_chain', None))
if resp.context:
    form = resp.context.get('form')
    if form:
        print('form errors', form.errors)
        print('non field errors', form.non_field_errors())
        print('cleaned', getattr(form, 'cleaned_data', None))
print('content snippet', resp.content.decode('utf-8')[:200])
