from collections import Counter
from datetime import date

from django.db.models import Avg, Q
from django.utils import timezone

from apps.appointments.models import Appointment, AppointmentStatus, AttendanceStatus
from apps.notifications.models import Notification
from apps.patient_treatments.models import PatientTreatment
from apps.payments.models import Payment, PaymentStatus
from apps.treatments.models import TreatmentCategory

FEATURE_NAMES = [
    "visit_miss_rate",
    "consecutive_misses",
    "days_since_last_visit",
    "treatment_completion_pct",
    "overdue_payment_days",
    "visit_progression",
    "treatment_type_encoding",
    "patient_age_band",
    "notification_response_rate",
    "avg_appointment_gap",
]

TREATMENT_CATEGORY_MAP = {
    TreatmentCategory.OTHER: 0,
    TreatmentCategory.ORTHODONTIC: 1,
    TreatmentCategory.RESTORATIVE: 2,
    TreatmentCategory.PREVENTIVE: 3,
    TreatmentCategory.SURGICAL: 4,
}


def _age_band(dob: date | None, today: date) -> int:
    if not dob:
        return 0
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    if age < 18:
        return 1
    if age < 30:
        return 2
    if age < 45:
        return 3
    if age < 60:
        return 4
    return 5


def build_patient_features(patient, now=None) -> dict:
    now = now or timezone.now()
    today = now.date()

    appointments = Appointment.objects.filter(patient=patient).order_by("scheduled_at")
    total_visits = appointments.count()
    missed_visits = appointments.filter(
        Q(attendance=AttendanceStatus.ABSENT) | Q(status=AppointmentStatus.NO_SHOW)
    ).count()
    completed_visits = appointments.filter(
        Q(attendance=AttendanceStatus.PRESENT) | Q(status=AppointmentStatus.COMPLETED)
    ).count()

    visit_miss_rate = missed_visits / total_visits if total_visits else 0.0
    visit_progression = completed_visits / total_visits if total_visits else 0.0

    recent_appointments = list(appointments.order_by("-scheduled_at")[:10])
    consecutive_misses = 0
    for appt in recent_appointments:
        missed = appt.attendance == AttendanceStatus.ABSENT or appt.status == AppointmentStatus.NO_SHOW
        if missed:
            consecutive_misses += 1
        else:
            break

    last_visit = appointments.filter(
        Q(attendance=AttendanceStatus.PRESENT) | Q(status=AppointmentStatus.COMPLETED)
    ).order_by("-scheduled_at").first()
    if last_visit:
        days_since_last_visit = max((now - last_visit.scheduled_at).days, 0)
    elif total_visits:
        days_since_last_visit = max((now - appointments.last().scheduled_at).days, 0)
    else:
        days_since_last_visit = 365

    treatment_qs = PatientTreatment.objects.filter(patient=patient).select_related("treatment")
    treatment_completion_pct = (
        treatment_qs.aggregate(avg=Avg("progress_percent"))["avg"] or 0.0
    )
    categories = list(treatment_qs.values_list("treatment__category", flat=True))
    top_category = Counter(categories).most_common(1)[0][0] if categories else TreatmentCategory.OTHER
    treatment_type_encoding = TREATMENT_CATEGORY_MAP.get(top_category, 0)

    overdue_payment_days = 0
    overdue_qs = Payment.objects.filter(
        patient=patient,
        status__in=[PaymentStatus.PENDING, PaymentStatus.FAILED],
    )
    if overdue_qs.exists():
        overdue_days = [
            max((today - p.payment_date).days, 0)
            for p in overdue_qs
            if p.payment_date
        ]
        overdue_payment_days = max(overdue_days) if overdue_days else 0

    notifications = Notification.objects.filter(user=patient.user)
    notification_total = notifications.count()
    notification_read = notifications.filter(is_read=True).count()
    notification_response_rate = (
        notification_read / notification_total if notification_total else 0.0
    )

    appt_times = list(appointments.values_list("scheduled_at", flat=True))
    if len(appt_times) >= 2:
        gaps = [
            max((appt_times[i] - appt_times[i - 1]).days, 0)
            for i in range(1, len(appt_times))
        ]
        avg_appointment_gap = sum(gaps) / len(gaps) if gaps else 0.0
    else:
        avg_appointment_gap = 0.0

    return {
        "visit_miss_rate": float(visit_miss_rate),
        "consecutive_misses": int(consecutive_misses),
        "days_since_last_visit": int(days_since_last_visit),
        "treatment_completion_pct": float(treatment_completion_pct),
        "overdue_payment_days": int(overdue_payment_days),
        "visit_progression": float(visit_progression),
        "treatment_type_encoding": int(treatment_type_encoding),
        "patient_age_band": int(_age_band(patient.date_of_birth, today)),
        "notification_response_rate": float(notification_response_rate),
        "avg_appointment_gap": float(avg_appointment_gap),
    }
