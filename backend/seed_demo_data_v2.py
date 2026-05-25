#!/usr/bin/env python
"""
Comprehensive demo data seeder for DentalAI.
Creates realistic patient stories, demo accounts, AI models, and analytics data.

Usage: python manage.py shell < seed_demo_data_v2.py
"""

import os
import django
from datetime import timedelta, datetime
from decimal import Decimal
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction

# Import all models
from apps.users.models import User, UserRole
from apps.patients.models import Patient
from apps.doctors.models import Doctor
from apps.appointments.models import Appointment, AppointmentStatus, AttendanceStatus
from apps.treatments.models import Treatment, TreatmentCategory
from apps.patient_treatments.models import PatientTreatment, TreatmentStatus
from apps.clinical_notes.models import ClinicalNote
from apps.payments.models import Payment, PaymentStatus, PaymentMethod
from apps.notifications.models import Notification, NotificationType
from apps.ai_predictions.models import ModelVersion, AIPrediction, RiskLevel, ShapExplanation, ModelType
from apps.ai_interventions.models import AIGeneratedMessage, MessageType, DeliveryStatus, DeliveryChannel, DeliveryTracking, InterventionLog, InterventionAction, InterventionOutcome

User = get_user_model()

# Constants
NOW = timezone.now()
DEMO_PASSWORD = "Demo1234!"  # Will be overridden by specific passwords

def create_user(email, role, first_name, last_name, phone="", password=None, is_active=True):
    """Create a user with specified role."""
    if password is None:
        password = DEMO_PASSWORD
    
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'first_name': first_name,
            'last_name': last_name,
            'role': role,
            'phone': phone,
            'is_active': is_active,
            'email_verified': True,
            'phone_verified': role != UserRole.PATIENT,
        }
    )
    if created:
        user.set_password(password)
        user.save()
        print(f"✓ Created {role} user: {email}")
    else:
        # Update password if user exists
        user.set_password(password)
        user.save()
        print(f"✓ Updated {role} user: {email}")
    
    return user

def create_demo_accounts():
    """Create demo accounts for all roles."""
    print("\n=== Creating Demo Accounts ===")
    
    # Admin
    admin_user = create_user(
        email="admin@dentalai.com",
        role=UserRole.ADMIN,
        first_name="Sarah",
        last_name="Admin",
        phone="+1-555-0001",
        password="Admin123!"
    )
    
    # Doctor
    doctor_user = create_user(
        email="doctor@dentalai.com",
        role=UserRole.DOCTOR,
        first_name="Dr. Emily",
        last_name="Chen",
        phone="+1-555-0002",
        password="Doctor123!"
    )
    Doctor.objects.get_or_create(
        user=doctor_user,
        defaults={
            'specialization': 'Orthodontics',
            'license_number': 'DOC-2024-001',
            'bio': 'Experienced orthodontist specializing in invisible aligners and comprehensive dental care.',
            'is_available': True
        }
    )
    
    # Receptionist
    receptionist_user = create_user(
        email="reception@dentalai.com",
        role=UserRole.RECEPTIONIST,
        first_name="Maria",
        last_name="Garcia",
        phone="+1-555-0003",
        password="Reception123!"
    )
    
    # Patient
    patient_user = create_user(
        email="patient@dentalai.com",
        role=UserRole.PATIENT,
        first_name="John",
        last_name="Smith",
        phone="+1-555-0004",
        password="Patient123!"
    )
    
    return admin_user, doctor_user, receptionist_user, patient_user

def create_treatment_catalog():
    """Create standard treatment catalog."""
    print("\n=== Creating Treatment Catalog ===")
    
    treatments_data = [
        {
            'name': 'Invisalign / Clear Aligners',
            'description': 'Clear aligner therapy for straightening teeth without traditional braces.',
            'category': TreatmentCategory.ORTHODONTIC,
            'duration_weeks': 52,
        },
        {
            'name': 'Traditional Braces',
            'description': 'Metal braces for comprehensive orthodontic treatment.',
            'category': TreatmentCategory.ORTHODONTIC,
            'duration_weeks': 78,
        },
        {
            'name': 'Dental Implant',
            'description': 'Surgical placement of titanium implant with crown restoration.',
            'category': TreatmentCategory.SURGICAL,
            'duration_weeks': 24,
        },
        {
            'name': 'Root Canal Therapy',
            'description': 'Endodontic treatment to save infected or damaged teeth.',
            'category': TreatmentCategory.RESTORATIVE,
            'duration_weeks': 4,
        },
        {
            'name': 'Dental Crown',
            'description': 'Custom crown to restore damaged or weakened teeth.',
            'category': TreatmentCategory.RESTORATIVE,
            'duration_weeks': 3,
        },
        {
            'name': 'Professional Cleaning',
            'description': 'Regular dental cleaning and preventive care.',
            'category': TreatmentCategory.PREVENTIVE,
            'duration_weeks': 1,
        },
        {
            'name': 'Teeth Whitening',
            'description': 'Professional whitening treatment for brighter smile.',
            'category': TreatmentCategory.PREVENTIVE,
            'duration_weeks': 2,
        },
    ]
    
    treatments = {}
    for data in treatments_data:
        treatment, created = Treatment.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        treatments[data['name']] = treatment
        if created:
            print(f"✓ Created treatment: {data['name']}")
    
    return treatments

def create_patient_story(patient_email, first_name, last_name, phone, story_type, doctor):
    """Create a complete patient story with all related data."""
    print(f"\n=== Creating Patient Story: {first_name} ({story_type}) ===")
    
    # Create user and patient
    user = create_user(
        email=patient_email,
        role=UserRole.PATIENT,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        password="Patient123!"
    )
    
    patient = Patient.objects.create(
        user=user,
        date_of_birth=NOW - timedelta(days=random.randint(7300, 14600)),  # 20-40 years old
        gender=random.choice(['male', 'female']),
        blood_group=random.choice(['A+', 'B+', 'O+', 'AB+', 'A-', 'B-', 'O-', 'AB-']),
        emergency_contact_name=f"Emergency Contact for {first_name}",
        emergency_contact_phone=f"+1-555-{random.randint(1000, 9999)}",
    )
    
    # Story-specific data
    if story_type == "high_risk_dropout":
        return create_high_risk_dropout_story(patient, doctor, NOW)
    elif story_type == "successful_intervention":
        return create_successful_intervention_story(patient, doctor, NOW)
    elif story_type == "missed_appointment":
        return create_missed_appointment_story(patient, doctor, NOW)
    elif story_type == "payment_risk":
        return create_payment_risk_story(patient, doctor, NOW)
    elif story_type == "improving_adherence":
        return create_improving_adherence_story(patient, doctor, NOW)

def create_high_risk_dropout_story(patient, doctor, now):
    """High-risk patient with multiple missed appointments."""
    print("  Creating high-risk dropout story...")
    
    treatment = Treatment.objects.get(name="Invisalign / Clear Aligners")
    PatientTreatment.objects.create(
        patient=patient,
        treatment=treatment,
        doctor=doctor,
        status=TreatmentStatus.ACTIVE,
        progress_percent=15,
        started_at=now - timedelta(days=90),
        notes="Patient showing signs of disengagement. Multiple missed appointments."
    )
    
    # Missed appointments
    Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        scheduled_at=now - timedelta(days=60),
        duration_minutes=30,
        status=AppointmentStatus.NO_SHOW,
        attendance=AttendanceStatus.ABSENT,
        reason="Regular checkup"
    )
    
    Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        scheduled_at=now - timedelta(days=30),
        duration_minutes=30,
        status=AppointmentStatus.CANCELLED,
        attendance=AttendanceStatus.ABSENT,
        reason="Follow-up"
    )
    
    # Future appointment
    Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        scheduled_at=now + timedelta(days=7),
        duration_minutes=30,
        status=AppointmentStatus.SCHEDULED,
        attendance=AttendanceStatus.PENDING,
        reason="Urgent follow-up"
    )
    
    # AI Prediction - High Risk
    prediction = AIPrediction.objects.create(
        patient=patient,
        model_version=get_active_model(),
        probability=0.85,
        risk_level=RiskLevel.HIGH,
        features={
            "missed_appointments": 2,
            "treatment_progress": 15,
            "days_since_last_visit": 60,
            "engagement_score": 0.2
        },
        prediction_source="batch"
    )
    
    # SHAP Explanation
    create_shap_explanation(prediction, patient, is_high_risk=True)
    
    # Intervention
    message = AIGeneratedMessage.objects.create(
        patient=patient,
        prediction=prediction,
        message_type=MessageType.MISSED_FOLLOWUP,
        language="en",
        content=f"Hi {patient.user.first_name}, we've noticed you've missed some important appointments for your Invisalign treatment. Consistent visits are crucial for achieving your dream smile. Please call us to reschedule your next appointment. We're here to help you succeed!",
        confidence_score=0.92,
        risk_level=RiskLevel.HIGH,
        risk_score=85,
        delivery_status=DeliveryStatus.QUEUED,
        personalization={
            "patient_name": patient.user.first_name,
            "treatment_type": "Invisalign",
            "missed_count": 2
        }
    )
    
    DeliveryTracking.objects.create(
        message=message,
        channel=DeliveryChannel.IN_APP,
        status=DeliveryStatus.QUEUED,
        attempt=1
    )
    
    # Notification
    Notification.objects.create(
        user=patient.user,
        title="Important: Missed Appointments",
        body="You have missed 2 appointments for your Invisalign treatment. Please contact us to reschedule.",
        notification_type=NotificationType.APPOINTMENT,
        metadata={"appointment_count": 2, "risk_level": "high"}
    )
    
    return patient

def create_successful_intervention_story(patient, doctor, now):
    """Patient who responded well to intervention."""
    print("  Creating successful intervention story...")
    
    treatment = Treatment.objects.get(name="Dental Implant")
    PatientTreatment.objects.create(
        patient=patient,
        treatment=treatment,
        doctor=doctor,
        status=TreatmentStatus.IN_PROGRESS,
        progress_percent=75,
        started_at=now - timedelta(days=120),
        notes="Excellent progress. Patient very compliant with post-op care."
    )
    
    # Past missed appointment
    Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        scheduled_at=now - timedelta(days=90),
        duration_minutes=60,
        status=AppointmentStatus.NO_SHOW,
        attendance=AttendanceStatus.ABSENT,
        reason="Implant checkup"
    )
    
    # Intervention sent
    old_prediction = AIPrediction.objects.create(
        patient=patient,
        model_version=get_active_model(),
        probability=0.75,
        risk_level=RiskLevel.HIGH,
        features={"missed_appointments": 1},
        prediction_source="batch"
    )
    
    message = AIGeneratedMessage.objects.create(
        patient=patient,
        prediction=old_prediction,
        message_type=MessageType.MOTIVATIONAL,
        language="en",
        content=f"Hi {patient.user.first_name}, we missed you at your implant checkup! Your smile transformation is important to us. Let's get you back on track for the perfect result you deserve.",
        confidence_score=0.88,
        risk_level=RiskLevel.HIGH,
        risk_score=75,
        delivery_status=DeliveryStatus.DELIVERED,
        personalization={"patient_name": patient.user.first_name}
    )
    
    DeliveryTracking.objects.create(
        message=message,
        channel=DeliveryChannel.IN_APP,
        status=DeliveryStatus.DELIVERED,
        attempt=1,
        delivered_at=now - timedelta(days=89)
    )
    
    InterventionLog.objects.create(
        patient=patient,
        message=message,
        action=InterventionAction.SENT,
        status=InterventionOutcome.SUCCESS,
        impact_score=0.65,
        notes="Patient responded positively to intervention"
    )
    
    # Recent completed appointments
    Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        scheduled_at=now - timedelta(days=60),
        duration_minutes=45,
        status=AppointmentStatus.COMPLETED,
        attendance=AttendanceStatus.PRESENT,
        reason="Follow-up after intervention"
    )
    
    Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        scheduled_at=now - timedelta(days=30),
        duration_minutes=30,
        status=AppointmentStatus.COMPLETED,
        attendance=AttendanceStatus.PRESENT,
        reason="Regular checkup"
    )
    
    # Current prediction - Low Risk (improved)
    new_prediction = AIPrediction.objects.create(
        patient=patient,
        model_version=get_active_model(),
        probability=0.25,
        risk_level=RiskLevel.LOW,
        features={
            "recent_attendance": True,
            "treatment_progress": 75,
            "engagement_score": 0.9
        },
        prediction_source="api"
    )
    
    create_shap_explanation(new_prediction, patient, is_high_risk=False)
    
    # Future appointment
    Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        scheduled_at=now + timedelta(days=14),
        duration_minutes=30,
        status=AppointmentStatus.CONFIRMED,
        attendance=AttendanceStatus.PENDING,
        reason="Final implant assessment"
    )
    
    # Payment
    Payment.objects.create(
        patient=patient,
        amount=Decimal("1250.00"),
        status=PaymentStatus.PAID,
        payment_date=now - timedelta(days=5),
        method=PaymentMethod.CARD,
        reference="TXN-2024-001",
        description="Implant procedure payment"
    )
    
    return patient

def create_missed_appointment_story(patient, doctor, now):
    """Patient who just missed an appointment today."""
    print("  Creating missed appointment story...")
    
    treatment = Treatment.objects.get(name="Root Canal Therapy")
    PatientTreatment.objects.create(
        patient=patient,
        treatment=treatment,
        doctor=doctor,
        status=TreatmentStatus.IN_PROGRESS,
        progress_percent=50,
        started_at=now - timedelta(days=14),
        notes="Mid-treatment, needs follow-up"
    )
    
    # Missed appointment today
    Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        scheduled_at=now - timedelta(hours=2),
        duration_minutes=45,
        status=AppointmentStatus.NO_SHOW,
        attendance=AttendanceStatus.ABSENT,
        reason="Root canal follow-up"
    )
    
    # Previous completed appointment
    Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        scheduled_at=now - timedelta(days=14),
        duration_minutes=60,
        status=AppointmentStatus.COMPLETED,
        attendance=AttendanceStatus.PRESENT,
        reason="Initial root canal"
    )
    
    # AI Prediction - Medium Risk
    prediction = AIPrediction.objects.create(
        patient=patient,
        model_version=get_active_model(),
        probability=0.55,
        risk_level=RiskLevel.MEDIUM,
        features={
            "missed_recent_appointment": True,
            "treatment_in_progress": True
        },
        prediction_source="api"
    )
    
    create_shap_explanation(prediction, patient, is_high_risk=False)
    
    # Immediate intervention
    message = AIGeneratedMessage.objects.create(
        patient=patient,
        prediction=prediction,
        message_type=MessageType.MISSED_FOLLOWUP,
        language="en",
        content=f"Hi {patient.user.first_name}, we noticed you missed your root canal follow-up appointment today. It's important to continue your treatment to avoid complications. Please call us as soon as possible to reschedule.",
        confidence_score=0.95,
        risk_level=RiskLevel.MEDIUM,
        risk_score=55,
        delivery_status=DeliveryStatus.SENT,
        personalization={"patient_name": patient.user.first_name}
    )
    
    DeliveryTracking.objects.create(
        message=message,
        channel=DeliveryChannel.SMS,
        status=DeliveryStatus.SENT,
        attempt=1
    )
    
    # Notification
    Notification.objects.create(
        user=patient.user,
        title="Missed Appointment Today",
        body="You missed your root canal follow-up. Please call us to reschedule urgently.",
        notification_type=NotificationType.APPOINTMENT,
        is_read=False
    )
    
    return patient

def create_payment_risk_story(patient, doctor, now):
    """Patient with payment issues."""
    print("  Creating payment risk story...")
    
    treatment = Treatment.objects.get(name="Dental Implant")
    PatientTreatment.objects.create(
        patient=patient,
        treatment=treatment,
        doctor=doctor,
        status=TreatmentStatus.ON_HOLD,
        progress_percent=90,
        started_at=now - timedelta(days=180),
        notes="Treatment on hold due to payment issues. Almost complete."
    )
    
    # Completed appointments
    Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        scheduled_at=now - timedelta(days=150),
        duration_minutes=90,
        status=AppointmentStatus.COMPLETED,
        attendance=AttendanceStatus.PRESENT,
        reason="Implant surgery"
    )
    
    Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        scheduled_at=now - timedelta(days=90),
        duration_minutes=30,
        status=AppointmentStatus.COMPLETED,
        attendance=AttendanceStatus.PRESENT,
        reason="Healing checkup"
    )
    
    # Overdue payment
    Payment.objects.create(
        patient=patient,
        amount=Decimal("2500.00"),
        status=PaymentStatus.PENDING,
        payment_date=now - timedelta(days=60),
        method=PaymentMethod.INSURANCE,
        reference="INV-2024-042",
        description="Final implant restoration - Payment overdue"
    )
    
    # AI Prediction - Medium Risk (payment-related)
    prediction = AIPrediction.objects.create(
        patient=patient,
        model_version=get_active_model(),
        probability=0.65,
        risk_level=RiskLevel.MEDIUM,
        features={
            "outstanding_balance": 2500,
            "payment_overdue_days": 60,
            "treatment_completion": 90
        },
        prediction_source="batch"
    )
    
    create_shap_explanation(prediction, patient, is_high_risk=False)
    
    # Intervention
    message = AIGeneratedMessage.objects.create(
        patient=patient,
        prediction=prediction,
        message_type=MessageType.TREATMENT_ENCOURAGEMENT,
        language="en",
        content=f"Hi {patient.user.first_name}, your dental implant treatment is 90% complete! We're excited to finish your beautiful new smile. Please contact our billing department to arrange payment for the final restoration. We offer flexible payment plans.",
        confidence_score=0.85,
        risk_level=RiskLevel.MEDIUM,
        risk_score=65,
        delivery_status=DeliveryStatus.DELIVERED,
        personalization={
            "patient_name": patient.user.first_name,
            "completion_percent": 90
        }
    )
    
    DeliveryTracking.objects.create(
        message=message,
        channel=DeliveryChannel.EMAIL,
        status=DeliveryStatus.DELIVERED,
        attempt=1,
        delivered_at=now - timedelta(days=5)
    )
    
    return patient

def create_improving_adherence_story(patient, doctor, now):
    """Patient showing improvement in adherence."""
    print("  Creating improving adherence story...")
    
    treatment = Treatment.objects.get(name="Traditional Braces")
    PatientTreatment.objects.create(
        patient=patient,
        treatment=treatment,
        doctor=doctor,
        status=TreatmentStatus.IN_PROGRESS,
        progress_percent=40,
        started_at=now - timedelta(days=120),
        notes="Showing great improvement in oral hygiene and appointment attendance."
    )
    
    # Past cancelled appointment
    Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        scheduled_at=now - timedelta(days=90),
        duration_minutes=30,
        status=AppointmentStatus.CANCELLED,
        attendance=AttendanceStatus.ABSENT,
        reason="Braces adjustment"
    )
    
    # Recent completed appointments (improving pattern)
    Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        scheduled_at=now - timedelta(days=60),
        duration_minutes=30,
        status=AppointmentStatus.COMPLETED,
        attendance=AttendanceStatus.PRESENT,
        reason="Braces adjustment"
    )
    
    Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        scheduled_at=now - timedelta(days=30),
        duration_minutes=30,
        status=AppointmentStatus.COMPLETED,
        attendance=AttendanceStatus.PRESENT,
        reason="Regular checkup"
    )
    
    # Clinical note
    ClinicalNote.objects.create(
        patient=patient,
        doctor=doctor,
        content="Excellent improvement in oral hygiene! Patient is now consistently brushing and flossing. Elastics compliance has improved significantly. Treatment progressing well.",
        visit_date=(now - timedelta(days=30)).date(),
        is_private=False
    )
    
    # Old prediction (higher risk)
    AIPrediction.objects.create(
        patient=patient,
        model_version=get_active_model(),
        probability=0.60,
        risk_level=RiskLevel.MEDIUM,
        features={"missed_appointments": 1},
        prediction_source="batch",
        created_at=now - timedelta(days=90)
    )
    
    # Current prediction (improved)
    current_prediction = AIPrediction.objects.create(
        patient=patient,
        model_version=get_active_model(),
        probability=0.30,
        risk_level=RiskLevel.LOW,
        features={
            "consecutive_attendance": 2,
            "hygiene_improvement": True,
            "treatment_progress": 40
        },
        prediction_source="api"
    )
    
    create_shap_explanation(current_prediction, patient, is_high_risk=False)
    
    # Future appointment
    Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        scheduled_at=now + timedelta(days=21),
        duration_minutes=30,
        status=AppointmentStatus.SCHEDULED,
        attendance=AttendanceStatus.PENDING,
        reason="Braces adjustment"
    )
    
    return patient

def get_active_model():
    """Get or create the active AI model version."""
    model, created = ModelVersion.objects.get_or_create(
        name="DentalAI Risk Predictor v2.1",
        defaults={
            'model_type': ModelType.XGBOOST,
            'is_active': True,
            'trained_at': NOW - timedelta(days=30),
            'metrics': {
                'accuracy': 0.89,
                'precision': 0.87,
                'recall': 0.85,
                'f1_score': 0.86,
                'auc_roc': 0.92
            },
            'calibration': {
                'method': 'isotonic',
                'log_loss': 0.32
            },
            'feature_names': [
                'missed_appointments',
                'treatment_progress',
                'days_since_last_visit',
                'engagement_score',
                'payment_status',
                'age',
                'treatment_type'
            ],
            'hyperparameters': {
                'n_estimators': 100,
                'max_depth': 6,
                'learning_rate': 0.1
            },
            'data_summary': {
                'training_samples': 5000,
                'features': 7,
                'target_distribution': {
                    'low_risk': 0.45,
                    'medium_risk': 0.35,
                    'high_risk': 0.20
                }
            },
            'model_path': '/models/xgboost_v2.1.json',
            'notes': 'Production model for dropout risk prediction'
        }
    )
    
    if created:
        print("✓ Created active AI model version")
    
    return model

def create_shap_explanation(prediction, patient, is_high_risk=False):
    """Create SHAP explanation for a prediction."""
    if is_high_risk:
        shap_values = {
            'missed_appointments': 0.35,
            'treatment_progress': -0.15,
            'days_since_last_visit': 0.25,
            'engagement_score': 0.20,
            'base_value': 0.20
        }
        top_features = [
            {'feature': 'missed_appointments', 'value': 2, 'impact': 0.35},
            {'feature': 'days_since_last_visit', 'value': 60, 'impact': 0.25},
            {'feature': 'engagement_score', 'value': 0.2, 'impact': 0.20}
        ]
        feature_values = {
            'missed_appointments': 2,
            'treatment_progress': 15,
            'days_since_last_visit': 60,
            'engagement_score': 0.2
        }
    else:
        shap_values = {
            'treatment_progress': -0.20,
            'engagement_score': -0.15,
            'missed_appointments': 0.10,
            'days_since_last_visit': 0.05,
            'base_value': 0.20
        }
        top_features = [
            {'feature': 'treatment_progress', 'value': 75, 'impact': -0.20},
            {'feature': 'engagement_score', 'value': 0.9, 'impact': -0.15},
            {'feature': 'missed_appointments', 'value': 0, 'impact': 0.10}
        ]
        feature_values = {
            'treatment_progress': prediction.features.get('treatment_progress', 50),
            'engagement_score': prediction.features.get('engagement_score', 0.5),
            'missed_appointments': prediction.features.get('missed_appointments', 0),
            'days_since_last_visit': prediction.features.get('days_since_last_visit', 30)
        }
    
    ShapExplanation.objects.create(
        prediction=prediction,
        patient=patient,
        model_version=prediction.model_version,
        base_value=shap_values['base_value'],
        shap_values=shap_values,
        top_features=top_features,
        feature_values=feature_values
    )

def create_additional_notifications(doctor, patients):
    """Create system-wide notifications."""
    print("\n=== Creating System Notifications ===")
    
    notifications = [
        {
            'user': patients[0].user,
            'title': 'Treatment Progress Update',
            'body': 'Your Invisalign treatment is progressing. Keep up the good work!',
            'type': NotificationType.TREATMENT,
        },
        {
            'user': patients[1].user,
            'title': 'Appointment Reminder',
            'body': 'Reminder: You have an appointment scheduled for tomorrow at 10:00 AM.',
            'type': NotificationType.APPOINTMENT,
            'is_read': True,
        },
        {
            'user': patients[2].user,
            'title': 'Payment Received',
            'body': 'Thank you for your payment of $1,250.00. Your account has been updated.',
            'type': NotificationType.PAYMENT,
            'is_read': True,
        },
        {
            'user': doctor.user,
            'title': 'New Patient Assigned',
            'body': 'You have been assigned a new patient: Alex Mercer.',
            'type': NotificationType.SYSTEM,
        },
        {
            'user': doctor.user,
            'title': 'High-Risk Alert',
            'body': 'Patient Alex Mercer has been flagged as high-risk for treatment dropout.',
            'type': NotificationType.SYSTEM,
            'is_read': False,
        },
    ]
    
    for notif_data in notifications:
        is_read = notif_data.pop('is_read', False)
        Notification.objects.create(
            **notif_data,
            is_read=is_read
        )
    
    print(f"✓ Created {len(notifications)} system notifications")

@transaction.atomic
def seed_all():
    """Main seeding function."""
    print("🚀 Starting DentalAI Demo Data Seeding...")
    print("=" * 60)
    
    # 1. Create demo accounts
    admin, doctor, receptionist, basic_patient = create_demo_accounts()
    
    # Get doctor profile
    doctor_profile = Doctor.objects.get(user=doctor)
    
    # 2. Create treatment catalog
    treatments = create_treatment_catalog()
    
    # 3. Create patient stories
    patient_stories = [
        ("alex.mercer@dentalai.com", "Alex", "Mercer", "+1-555-1001", "high_risk_dropout"),
        ("sarah.connor@dentalai.com", "Sarah", "Connor", "+1-555-1002", "successful_intervention"),
        ("john.doe@dentalai.com", "John", "Doe", "+1-555-1003", "missed_appointment"),
        ("emily.chen@dentalai.com", "Emily", "Chen", "+1-555-1004", "payment_risk"),
        ("michael.scott@dentalai.com", "Michael", "Scott", "+1-555-1005", "improving_adherence"),
    ]
    
    patients = []
    for email, first, last, phone, story_type in patient_stories:
        patient = create_patient_story(email, first, last, phone, story_type, doctor_profile)
        patients.append(patient)
    
    # 4. Create additional notifications
    create_additional_notifications(doctor, patients)
    
    # 5. Create some general analytics data
    print("\n=== Creating Analytics Data ===")
    
    # Add more appointments for analytics
    for i in range(10):
        patient = random.choice(patients)
        days_ago = random.randint(1, 30)
        Appointment.objects.create(
            patient=patient,
            doctor=doctor_profile,
            scheduled_at=now - timedelta(days=days_ago),
            duration_minutes=random.choice([30, 45, 60]),
            status=random.choice([AppointmentStatus.COMPLETED, AppointmentStatus.NO_SHOW]),
            attendance=random.choice([AttendanceStatus.PRESENT, AttendanceStatus.ABSENT]),
            reason="General checkup"
        )
    
    print("✓ Created additional analytics appointments")
    
    print("\n" + "=" * 60)
    print("✅ Demo data seeding completed successfully!")
    print("=" * 60)
    print("\n📋 Demo Accounts:")
    print(f"   Admin:       admin@dentalai.com       / Admin123!")
    print(f"   Doctor:      doctor@dentalai.com      / Doctor123!")
    print(f"   Reception:   reception@dentalai.com   / Reception123!")
    print(f"   Patient:     patient@dentalai.com     / Patient123!")
    print("\n📊 Data Created:")
    print(f"   • {User.objects.count()} users")
    print(f"   • {Patient.objects.count()} patients")
    print(f"   • {Doctor.objects.count()} doctors")
    print(f"   • {Treatment.objects.count()} treatments")
    print(f"   • {PatientTreatment.objects.count()} patient treatments")
    print(f"   • {Appointment.objects.count()} appointments")
    print(f"   • {AIPrediction.objects.count()} AI predictions")
    print(f"   • {ShapExplanation.objects.count()} SHAP explanations")
    print(f"   • {AIGeneratedMessage.objects.count()} AI messages")
    print(f"   • {Notification.objects.count()} notifications")
    print(f"   • {Payment.objects.count()} payments")
    print("\n🎯 Patient Stories:")
    print("   1. Alex Mercer - High-risk dropout (85% risk)")
    print("   2. Sarah Connor - Successful intervention (25% risk)")
    print("   3. John Doe - Missed appointment today (55% risk)")
    print("   4. Emily Chen - Payment risk (65% risk)")
    print("   5. Michael Scott - Improving adherence (30% risk)")
    print("\n🚀 Ready for demo!")

if __name__ == "__main__":
    seed_all()