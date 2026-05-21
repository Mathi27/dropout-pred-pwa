import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User, UserRole
from apps.patients.models import Patient, PatientTreatment, Treatment, ClinicalNote
from apps.appointments.models import Appointment
from apps.ai.models import AIPrediction, AIGeneratedMessage

def create_patient(email, first_name, last_name, phone):
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'first_name': first_name,
            'last_name': last_name,
            'role': UserRole.PATIENT,
            'phone': phone,
        }
    )
    if created:
        user.set_password("demo1234")
        user.save()
    patient, _ = Patient.objects.get_or_create(user=user)
    return patient

def create_demo_data():
    doctor = User.objects.filter(role=UserRole.DOCTOR).first()
    if not doctor:
        print("No doctor found. Please create one first.")
        return

    now = timezone.now()
    t_braces, _ = Treatment.objects.get_or_create(name="Invisalign / Braces", defaults={"description": "Orthodontic treatment", "duration_weeks": 52})
    t_implant, _ = Treatment.objects.get_or_create(name="Dental Implant", defaults={"description": "Surgical implant", "duration_weeks": 24})
    t_root, _ = Treatment.objects.get_or_create(name="Root Canal", defaults={"description": "Endodontic therapy", "duration_weeks": 4})

    print("Seeding 1. High-risk dropout patient...")
    p1 = create_patient("highrisk@demo.com", "Alex", "Mercer", "555-0101")
    PatientTreatment.objects.get_or_create(patient=p1, treatment=t_braces, defaults={"status": "active", "progress_percent": 15})
    # Missed appointments
    Appointment.objects.get_or_create(patient=p1, doctor=doctor.doctor_profile, scheduled_at=now - timedelta(days=14), defaults={"status": "no_show", "attendance": "absent", "duration_minutes": 30})
    Appointment.objects.get_or_create(patient=p1, doctor=doctor.doctor_profile, scheduled_at=now - timedelta(days=7), defaults={"status": "cancelled", "attendance": "absent", "duration_minutes": 30})
    AIPrediction.objects.create(patient=p1, risk_score=85, risk_level="high", probability=0.85, prediction_date=now - timedelta(days=1), features_used={"missed_visits": 2})

    print("Seeding 2. Successful intervention patient...")
    p2 = create_patient("success@demo.com", "Sarah", "Connor", "555-0102")
    PatientTreatment.objects.get_or_create(patient=p2, treatment=t_implant, defaults={"status": "active", "progress_percent": 60})
    Appointment.objects.get_or_create(patient=p2, doctor=doctor.doctor_profile, scheduled_at=now - timedelta(days=30), defaults={"status": "no_show", "attendance": "absent", "duration_minutes": 60})
    AIPrediction.objects.create(patient=p2, risk_score=75, risk_level="high", probability=0.75, prediction_date=now - timedelta(days=29), features_used={})
    AIGeneratedMessage.objects.create(patient=p2, message_type="motivational", content="Hi Sarah, we missed you at your last implant checkup. Let's get you back on track for a perfect smile!", delivery_status="delivered", sent_at=now - timedelta(days=28), confidence_score=0.9)
    Appointment.objects.get_or_create(patient=p2, doctor=doctor.doctor_profile, scheduled_at=now - timedelta(days=10), defaults={"status": "completed", "attendance": "present", "duration_minutes": 30})
    Appointment.objects.get_or_create(patient=p2, doctor=doctor.doctor_profile, scheduled_at=now + timedelta(days=10), defaults={"status": "pending", "attendance": "pending", "duration_minutes": 30})
    AIPrediction.objects.create(patient=p2, risk_score=25, risk_level="low", probability=0.25, prediction_date=now - timedelta(days=1), features_used={"recent_attendance": True})

    print("Seeding 3. Missed-appointment patient...")
    p3 = create_patient("missed@demo.com", "John", "Doe", "555-0103")
    PatientTreatment.objects.get_or_create(patient=p3, treatment=t_root, defaults={"status": "active", "progress_percent": 50})
    Appointment.objects.get_or_create(patient=p3, doctor=doctor.doctor_profile, scheduled_at=now - timedelta(hours=2), defaults={"status": "no_show", "attendance": "absent", "duration_minutes": 45})
    AIGeneratedMessage.objects.create(patient=p3, message_type="missed_followup", content="Hi John, it looks like you missed your root canal follow-up today. Please call us to reschedule.", delivery_status="delivered", sent_at=now - timedelta(hours=1), confidence_score=0.88)
    AIPrediction.objects.create(patient=p3, risk_score=55, risk_level="medium", probability=0.55, prediction_date=now, features_used={"missed_recent": True})

    print("Seeding 4. Payment-risk patient...")
    p4 = create_patient("payment@demo.com", "Emily", "Chen", "555-0104")
    PatientTreatment.objects.get_or_create(patient=p4, treatment=t_implant, defaults={"status": "active", "progress_percent": 90})
    Appointment.objects.get_or_create(patient=p4, doctor=doctor.doctor_profile, scheduled_at=now - timedelta(days=45), defaults={"status": "completed", "attendance": "present", "duration_minutes": 60})
    # Simulating payment risk implicitly by AI score
    AIPrediction.objects.create(patient=p4, risk_score=65, risk_level="medium", probability=0.65, prediction_date=now - timedelta(days=2), features_used={"outstanding_balance": True})

    print("Seeding 5. Improving adherence patient...")
    p5 = create_patient("improve@demo.com", "Michael", "Scott", "555-0105")
    PatientTreatment.objects.get_or_create(patient=p5, treatment=t_braces, defaults={"status": "active", "progress_percent": 40})
    Appointment.objects.get_or_create(patient=p5, doctor=doctor.doctor_profile, scheduled_at=now - timedelta(days=60), defaults={"status": "cancelled", "attendance": "absent", "duration_minutes": 30})
    Appointment.objects.get_or_create(patient=p5, doctor=doctor.doctor_profile, scheduled_at=now - timedelta(days=20), defaults={"status": "completed", "attendance": "present", "duration_minutes": 30})
    Appointment.objects.get_or_create(patient=p5, doctor=doctor.doctor_profile, scheduled_at=now - timedelta(days=2), defaults={"status": "completed", "attendance": "present", "duration_minutes": 30})
    ClinicalNote.objects.create(patient=p5, doctor=doctor.doctor_profile, content="Patient has improved oral hygiene significantly. Elastics are being worn properly.", visit_date=(now - timedelta(days=2)).date())
    AIPrediction.objects.create(patient=p5, risk_score=30, risk_level="low", probability=0.30, prediction_date=now, features_used={"consecutive_attendance": 2})

    print("Demo data seeded successfully!")

if __name__ == "__main__":
    create_demo_data()
