from django.db.models import Q
from django.utils import timezone

from apps.ai_predictions.services.features import build_patient_features
from apps.appointments.models import Appointment, AppointmentStatus, AttendanceStatus
from apps.patient_treatments.models import PatientTreatment, TreatmentStatus


def build_patient_context(patient):
    features = build_patient_features(patient)
    appointments = Appointment.objects.filter(patient=patient).order_by("scheduled_at")
    missed_visits = appointments.filter(
        Q(attendance=AttendanceStatus.ABSENT) | Q(status=AppointmentStatus.NO_SHOW)
    ).count()
    upcoming = appointments.filter(scheduled_at__gte=timezone.now()).order_by("scheduled_at").first()

    recent_appts = list(appointments.order_by("-scheduled_at")[:5])
    consecutive_misses = 0
    for appt in recent_appts:
        missed = appt.attendance == AttendanceStatus.ABSENT or appt.status == AppointmentStatus.NO_SHOW
        if missed:
            consecutive_misses += 1
        else:
            break

    treatment = (
        PatientTreatment.objects.filter(patient=patient)
        .select_related("treatment", "doctor__user")
        .order_by("-created_at")
        .first()
    )

    doctor_name = None
    if treatment and treatment.doctor:
        doctor_name = treatment.doctor.user.full_name
    elif appointments.exists() and appointments.last().doctor:
        doctor_name = appointments.last().doctor.user.full_name

    treatment_name = treatment.treatment.name if treatment else "your treatment plan"
    treatment_stage = treatment.status if treatment else "active"

    return {
        "features": features,
        "missed_visits": missed_visits,
        "consecutive_misses": consecutive_misses,
        "upcoming_appointment": upcoming,
        "treatment_name": treatment_name,
        "treatment_stage": treatment_stage,
        "doctor_name": doctor_name or "your care team",
    }
