import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.appointments.models import Appointment, AppointmentStatus, AttendanceStatus
from apps.doctors.models import Doctor
from apps.notifications.models import Notification, NotificationType
from apps.patients.models import Gender, Patient
from apps.patient_treatments.models import PatientTreatment, TreatmentStatus
from apps.payments.models import Payment, PaymentMethod, PaymentStatus
from apps.treatments.models import Treatment, TreatmentCategory
from apps.users.models import UserRole

User = get_user_model()

FIRST_NAMES = [
    "Aarav",
    "Vihaan",
    "Arjun",
    "Isha",
    "Anaya",
    "Kavya",
    "Riya",
    "Neha",
    "Aditya",
    "Rahul",
    "Sonia",
    "Meera",
    "Rohan",
    "Tanvi",
    "Kabir",
    "Nisha",
]

LAST_NAMES = [
    "Sharma",
    "Verma",
    "Patel",
    "Singh",
    "Mehta",
    "Iyer",
    "Nair",
    "Gupta",
    "Khan",
    "Joshi",
    "Das",
    "Kapoor",
]

SPECIALIZATIONS = [
    "Orthodontics",
    "Restorative Dentistry",
    "Periodontics",
    "Oral Surgery",
    "Pediatric Dentistry",
]

TREATMENT_TEMPLATES = [
    {"name": "Clear Aligners", "category": TreatmentCategory.ORTHODONTIC, "duration_weeks": 24},
    {"name": "Braces Plan", "category": TreatmentCategory.ORTHODONTIC, "duration_weeks": 32},
    {"name": "Root Canal", "category": TreatmentCategory.RESTORATIVE, "duration_weeks": 8},
    {"name": "Composite Filling", "category": TreatmentCategory.RESTORATIVE, "duration_weeks": 4},
    {"name": "Scaling + Polishing", "category": TreatmentCategory.PREVENTIVE, "duration_weeks": 6},
    {"name": "Wisdom Tooth Extraction", "category": TreatmentCategory.SURGICAL, "duration_weeks": 10},
    {"name": "Implant Prep", "category": TreatmentCategory.SURGICAL, "duration_weeks": 20},
    {"name": "Night Guard", "category": TreatmentCategory.OTHER, "duration_weeks": 6},
]

RISK_WEIGHTS = [
    ("high", 0.2),
    ("medium", 0.3),
    ("low", 0.5),
]


def _get_or_create_user(email: str, defaults: dict):
    user, created = User.objects.get_or_create(email=email, defaults=defaults)
    if created:
        user.set_unusable_password()
        user.save(update_fields=["password"])
    return user, created


def _ensure_treatments():
    treatments = list(Treatment.objects.all())
    if treatments:
        return treatments
    for template in TREATMENT_TEMPLATES:
        Treatment.objects.get_or_create(
            name=template["name"],
            defaults={
                "category": template["category"],
                "duration_weeks": template["duration_weeks"],
                "description": f"{template['name']} package",
            },
        )
    return list(Treatment.objects.all())


def _unique_license_number(rng: random.Random, used: set[str]) -> str:
    while True:
        candidate = f"LIC-{rng.randint(1000, 9999)}"
        if candidate not in used:
            used.add(candidate)
            return candidate


def _ensure_doctors(rng: random.Random, count: int):
    doctors = list(Doctor.objects.select_related("user"))
    doctor_ids = {doctor.id for doctor in doctors}
    used_license_numbers = set(
        Doctor.objects.exclude(license_number="").values_list("license_number", flat=True)
    )

    idx = 1
    while len(doctors) < count:
        email = f"doctor{idx}@clinic.local"
        idx += 1
        user, created = _get_or_create_user(
            email,
            {
                "role": UserRole.DOCTOR,
                "first_name": rng.choice(FIRST_NAMES),
                "last_name": rng.choice(LAST_NAMES),
                "is_staff": True,
            },
        )
        if not created and user.role != UserRole.DOCTOR:
            continue

        doctor, _ = Doctor.objects.get_or_create(
            user=user,
            defaults={
                "specialization": rng.choice(SPECIALIZATIONS),
                "license_number": _unique_license_number(rng, used_license_numbers),
            },
        )
        if doctor.id not in doctor_ids:
            doctors.append(doctor)
            doctor_ids.add(doctor.id)
    return doctors


def _risk_bucket(rng: random.Random) -> str:
    labels, weights = zip(*RISK_WEIGHTS)
    return rng.choices(labels, weights=weights, k=1)[0]


def _dropout_flag(rng: random.Random, risk: str) -> bool:
    rates = {
        "high": 0.45,
        "medium": 0.25,
        "low": 0.1,
    }
    return rng.random() < rates.get(risk, 0.2)


def _behavior_profile(rng: random.Random, risk: str, dropout: bool) -> dict:
    if dropout:
        return {
            "appt_count_range": (4, 9),
            "gap_range": (21, 45),
            "miss_prob": 0.5,
            "miss_streak": (2, 4),
            "last_completed_days": (60, 140),
            "last_scheduled_days": (5, 25),
            "payment_weights": (0.2, 0.55, 0.25),
            "payment_age_range": (30, 120),
            "treatment_progress_range": (5, 40),
            "treatment_statuses": [
                TreatmentStatus.IN_PROGRESS,
                TreatmentStatus.ON_HOLD,
                TreatmentStatus.CANCELLED,
            ],
            "treatment_start_range": (80, 240),
            "notification_read_range": (0.1, 0.35),
            "cancel_chance": 0.6,
            "cancel_prob": 0.2,
            "reschedule_prob": 0.15,
            "upcoming_prob": 0.1,
        }

    if risk == "high":
        return {
            "appt_count_range": (4, 10),
            "gap_range": (14, 35),
            "miss_prob": 0.3,
            "miss_streak": (1, 2),
            "last_completed_days": (30, 70),
            "last_scheduled_days": (3, 14),
            "payment_weights": (0.45, 0.4, 0.15),
            "payment_age_range": (14, 60),
            "treatment_progress_range": (30, 70),
            "treatment_statuses": [
                TreatmentStatus.ACTIVE,
                TreatmentStatus.IN_PROGRESS,
                TreatmentStatus.ON_HOLD,
            ],
            "treatment_start_range": (60, 200),
            "notification_read_range": (0.35, 0.6),
            "cancel_chance": 0.25,
            "cancel_prob": 0.12,
            "reschedule_prob": 0.1,
            "upcoming_prob": 0.25,
        }

    if risk == "medium":
        return {
            "appt_count_range": (5, 11),
            "gap_range": (10, 28),
            "miss_prob": 0.18,
            "miss_streak": (0, 2),
            "last_completed_days": (12, 40),
            "last_scheduled_days": (1, 10),
            "payment_weights": (0.7, 0.22, 0.08),
            "payment_age_range": (5, 30),
            "treatment_progress_range": (45, 85),
            "treatment_statuses": [
                TreatmentStatus.ACTIVE,
                TreatmentStatus.IN_PROGRESS,
                TreatmentStatus.COMPLETED,
            ],
            "treatment_start_range": (40, 160),
            "notification_read_range": (0.55, 0.75),
            "cancel_chance": 0.1,
            "cancel_prob": 0.08,
            "reschedule_prob": 0.08,
            "upcoming_prob": 0.35,
        }

    return {
        "appt_count_range": (6, 12),
        "gap_range": (7, 21),
        "miss_prob": 0.08,
        "miss_streak": (0, 1),
        "last_completed_days": (2, 14),
        "last_scheduled_days": (0, 7),
        "payment_weights": (0.85, 0.12, 0.03),
        "payment_age_range": (2, 18),
        "treatment_progress_range": (70, 100),
        "treatment_statuses": [
            TreatmentStatus.ACTIVE,
            TreatmentStatus.COMPLETED,
        ],
        "treatment_start_range": (30, 120),
        "notification_read_range": (0.75, 0.92),
        "cancel_chance": 0.05,
        "cancel_prob": 0.05,
        "reschedule_prob": 0.06,
        "upcoming_prob": 0.5,
    }


@transaction.atomic
def generate_synthetic_data(
    *,
    num_patients: int = 1200,
    num_doctors: int = 12,
    seed: int = 42,
) -> dict:
    rng = random.Random(seed)
    treatments = _ensure_treatments()
    doctors = _ensure_doctors(rng, num_doctors)

    appointment_batch = []
    payment_batch = []
    notification_batch = []
    treatment_batch = []

    patients_to_seed = []
    patient_profiles = {}
    now = timezone.now()
    for idx in range(1, num_patients + 1):
        email = f"patient{idx}@example.local"
        user, created = _get_or_create_user(
            email,
            {
                "role": UserRole.PATIENT,
                "first_name": rng.choice(FIRST_NAMES),
                "last_name": rng.choice(LAST_NAMES),
                "phone": f"9{rng.randint(100000000, 999999999)}",
            },
        )
        if not created and user.role != UserRole.PATIENT:
            continue

        age = rng.randint(18, 70)
        dob = timezone.now().date() - timedelta(days=age * 365 + rng.randint(0, 364))
        patient, patient_created = Patient.objects.get_or_create(
            user=user,
            defaults={
                "date_of_birth": dob,
                "gender": rng.choice([Gender.MALE, Gender.FEMALE, Gender.OTHER]),
                "address": f"{rng.randint(12, 98)} Market Street",
            },
        )
        needs = {
            "treatments": not patient.patient_treatments.exists(),
            "appointments": not patient.appointments.exists(),
            "payments": not patient.payments.exists(),
            "notifications": not patient.user.notifications.exists(),
        }
        if any(needs.values()):
            if patient.id not in patient_profiles:
                risk = _risk_bucket(rng)
                dropout = _dropout_flag(rng, risk)
                patient_profiles[patient.id] = {"risk": risk, "dropout": dropout}
            patients_to_seed.append((patient, needs))

    for patient, needs in patients_to_seed:
        profile = patient_profiles.get(patient.id)
        if not profile:
            continue
        risk = profile["risk"]
        dropout = profile["dropout"]
        behavior = _behavior_profile(rng, risk, dropout)

        if needs["treatments"]:
            treatment_count = rng.randint(1, 3)
            cancel_forced = rng.random() < behavior["cancel_chance"]
            cancel_used = False
            for _ in range(treatment_count):
                treatment = rng.choice(treatments)
                if cancel_forced and not cancel_used:
                    status = TreatmentStatus.CANCELLED
                    cancel_used = True
                else:
                    status = rng.choice(behavior["treatment_statuses"])

                if status in (TreatmentStatus.CANCELLED, TreatmentStatus.ON_HOLD):
                    progress = rng.randint(5, 35)
                elif status == TreatmentStatus.COMPLETED:
                    progress = rng.randint(80, 100)
                else:
                    progress = rng.randint(*behavior["treatment_progress_range"])

                started_at = now.date() - timedelta(days=rng.randint(*behavior["treatment_start_range"]))
                completed_at = None
                if status == TreatmentStatus.COMPLETED:
                    completed_at = started_at + timedelta(days=rng.randint(60, 160))
                treatment_batch.append(
                    PatientTreatment(
                        patient=patient,
                        treatment=treatment,
                        doctor=rng.choice(doctors),
                        status=status,
                        progress_percent=progress,
                        started_at=started_at,
                        completed_at=completed_at,
                    )
                )

        if needs["appointments"]:
            appt_count = rng.randint(*behavior["appt_count_range"])
            miss_streak = rng.randint(*behavior["miss_streak"])
            miss_streak = min(miss_streak, max(appt_count - 1, 0))
            completed_count = max(1, appt_count - miss_streak)
            gap_min, gap_max = behavior["gap_range"]
            last_completed_days = rng.randint(*behavior["last_completed_days"])
            last_scheduled_days = rng.randint(*behavior["last_scheduled_days"])
            last_completed_date = now - timedelta(days=last_completed_days)

            completed_dates = [last_completed_date]
            for _ in range(completed_count - 1):
                gap_days = rng.randint(gap_min, gap_max)
                completed_dates.append(completed_dates[-1] - timedelta(days=gap_days))
            completed_dates = sorted(completed_dates)

            miss_dates = []
            if miss_streak:
                current = last_completed_date
                for _ in range(miss_streak):
                    gap_days = rng.randint(max(3, gap_min // 2), gap_max)
                    current = current + timedelta(days=gap_days)
                    miss_dates.append(current)
                target_last = now - timedelta(days=last_scheduled_days)
                shift = target_last - miss_dates[-1]
                miss_dates = [d + shift for d in miss_dates]
                if miss_dates[0] <= last_completed_date:
                    adjust = last_completed_date + timedelta(days=gap_min) - miss_dates[0]
                    miss_dates = [d + adjust for d in miss_dates]

            for idx, scheduled_at in enumerate(completed_dates):
                if rng.random() < behavior["cancel_prob"]:
                    appointment_batch.append(
                        Appointment(
                            patient=patient,
                            doctor=rng.choice(doctors),
                            scheduled_at=scheduled_at,
                            duration_minutes=rng.choice([30, 40, 50, 60]),
                            status=AppointmentStatus.CANCELLED,
                            attendance=AttendanceStatus.PENDING,
                            reason=rng.choice(["Consult", "Follow-up", "Cleaning", "Review"]),
                        )
                    )
                    continue

                if rng.random() < behavior["reschedule_prob"]:
                    appointment_batch.append(
                        Appointment(
                            patient=patient,
                            doctor=rng.choice(doctors),
                            scheduled_at=scheduled_at,
                            duration_minutes=rng.choice([30, 40, 50, 60]),
                            status=AppointmentStatus.RESCHEDULED,
                            attendance=AttendanceStatus.PENDING,
                            reason=rng.choice(["Consult", "Follow-up", "Cleaning", "Review"]),
                        )
                    )
                    rescheduled_at = scheduled_at + timedelta(days=rng.randint(2, 10))
                    if rescheduled_at > now:
                        res_status = AppointmentStatus.SCHEDULED
                        res_attendance = AttendanceStatus.PENDING
                    else:
                        res_status = AppointmentStatus.COMPLETED
                        res_attendance = AttendanceStatus.PRESENT
                    appointment_batch.append(
                        Appointment(
                            patient=patient,
                            doctor=rng.choice(doctors),
                            scheduled_at=rescheduled_at,
                            duration_minutes=rng.choice([30, 40, 50, 60]),
                            status=res_status,
                            attendance=res_attendance,
                            reason=rng.choice(["Consult", "Follow-up", "Cleaning", "Review"]),
                        )
                    )
                    continue

                allow_miss = idx < len(completed_dates) - 1
                missed = allow_miss and rng.random() < behavior["miss_prob"]
                if missed:
                    attendance = AttendanceStatus.ABSENT
                    status = AppointmentStatus.NO_SHOW
                else:
                    attendance = AttendanceStatus.PRESENT
                    status = AppointmentStatus.COMPLETED
                appointment_batch.append(
                    Appointment(
                        patient=patient,
                        doctor=rng.choice(doctors),
                        scheduled_at=scheduled_at,
                        duration_minutes=rng.choice([30, 40, 50, 60]),
                        status=status,
                        attendance=attendance,
                        reason=rng.choice(["Consult", "Follow-up", "Cleaning", "Review"]),
                    )
                )

            for scheduled_at in miss_dates:
                appointment_batch.append(
                    Appointment(
                        patient=patient,
                        doctor=rng.choice(doctors),
                        scheduled_at=scheduled_at,
                        duration_minutes=rng.choice([30, 40, 50, 60]),
                        status=AppointmentStatus.NO_SHOW,
                        attendance=AttendanceStatus.ABSENT,
                        reason=rng.choice(["Consult", "Follow-up", "Cleaning", "Review"]),
                    )
                )

            if rng.random() < behavior["upcoming_prob"]:
                upcoming_at = now + timedelta(days=rng.randint(2, 21))
                appointment_batch.append(
                    Appointment(
                        patient=patient,
                        doctor=rng.choice(doctors),
                        scheduled_at=upcoming_at,
                        duration_minutes=rng.choice([30, 40, 50, 60]),
                        status=AppointmentStatus.SCHEDULED,
                        attendance=AttendanceStatus.PENDING,
                        reason=rng.choice(["Consult", "Follow-up", "Cleaning", "Review"]),
                    )
                )

        if needs["payments"]:
            payment_count = rng.randint(1, 3)
            paid_w, pending_w, failed_w = behavior["payment_weights"]
            for _ in range(payment_count):
                status = rng.choices(
                    [PaymentStatus.PAID, PaymentStatus.PENDING, PaymentStatus.FAILED],
                    weights=[paid_w, pending_w, failed_w],
                    k=1,
                )[0]
                payment_batch.append(
                    Payment(
                        patient=patient,
                        amount=rng.randint(800, 6000),
                        status=status,
                        payment_date=now.date()
                        - timedelta(days=rng.randint(*behavior["payment_age_range"])),
                        method=rng.choice([PaymentMethod.CARD, PaymentMethod.UPI, PaymentMethod.CASH]),
                        description="Treatment installment",
                    )
                )

        if needs["notifications"]:
            notif_count = rng.randint(4, 10)
            read_prob = rng.uniform(*behavior["notification_read_range"])
            for _ in range(notif_count):
                is_read = rng.random() < read_prob
                notification_batch.append(
                    Notification(
                        user=patient.user,
                        title=rng.choice(["Upcoming visit", "Payment reminder", "Check-in", "Plan update"]),
                        body="Automated reminder from DentalAI",
                        notification_type=rng.choice(list(NotificationType.values)),
                        is_read=is_read,
                        read_at=now if is_read else None,
                        metadata={"channel": "email"},
                    )
                )

        if len(appointment_batch) >= 4000:
            Appointment.objects.bulk_create(appointment_batch)
            appointment_batch = []
        if len(payment_batch) >= 4000:
            Payment.objects.bulk_create(payment_batch)
            payment_batch = []
        if len(notification_batch) >= 4000:
            Notification.objects.bulk_create(notification_batch)
            notification_batch = []
        if len(treatment_batch) >= 4000:
            PatientTreatment.objects.bulk_create(treatment_batch)
            treatment_batch = []

    if appointment_batch:
        Appointment.objects.bulk_create(appointment_batch)
    if payment_batch:
        Payment.objects.bulk_create(payment_batch)
    if notification_batch:
        Notification.objects.bulk_create(notification_batch)
    if treatment_batch:
        PatientTreatment.objects.bulk_create(treatment_batch)

    return {
        "patients": num_patients,
        "appointments": Appointment.objects.count(),
        "payments": Payment.objects.count(),
        "notifications": Notification.objects.count(),
        "patient_treatments": PatientTreatment.objects.count(),
    }
