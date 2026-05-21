from __future__ import annotations

from datetime import timedelta

from django.db.models import Avg, Q
from django.utils import timezone

from apps.ai_interventions.models import AIGeneratedMessage
from apps.ai_predictions.models import AIPrediction
from apps.ai_predictions.services.features import build_patient_features
from apps.ai_predictions.services.timeline import build_patient_timeline
from apps.appointments.models import Appointment, AppointmentStatus, AttendanceStatus
from apps.notifications.models import Notification
from apps.patient_treatments.models import PatientTreatment, TreatmentStatus


def _adherence_score(features: dict) -> float:
    miss_rate = features.get("visit_miss_rate", 0)
    progression = features.get("visit_progression", 0)
    treatment_completion = features.get("treatment_completion_pct", 0) / 100
    notification_rate = features.get("notification_response_rate", 0)
    overdue_days = features.get("overdue_payment_days", 0)

    overdue_penalty = min(overdue_days / 90, 1) * 0.15
    raw = (
        0.45 * (1 - miss_rate)
        + 0.25 * progression
        + 0.2 * treatment_completion
        + 0.1 * notification_rate
        - overdue_penalty
    )
    score = max(0.0, min(raw, 1.0))
    return round(score * 100, 1)


def _adherence_stage(score: float) -> str:
    if score >= 80:
        return "on_track"
    if score >= 60:
        return "watchlist"
    return "at_risk"


def build_patient_journey(patient, days: int = 180) -> dict:
    now = timezone.now()
    since = now - timedelta(days=days)

    appointments = Appointment.objects.filter(patient=patient)
    total_appts = appointments.count()
    missed_appts = appointments.filter(
        Q(status=AppointmentStatus.NO_SHOW) | Q(attendance=AttendanceStatus.ABSENT)
    ).count()
    cancelled_appts = appointments.filter(status=AppointmentStatus.CANCELLED).count()
    completed_appts = appointments.filter(status=AppointmentStatus.COMPLETED).count()
    upcoming_appts = appointments.filter(
        scheduled_at__gte=now,
        status__in=[AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED],
    ).count()

    recent_appointments = []
    for appt in appointments.select_related("doctor", "doctor__user").order_by("-scheduled_at")[:6]:
        recent_appointments.append(
            {
                "id": str(appt.id),
                "scheduled_at": appt.scheduled_at.isoformat(),
                "status": appt.status,
                "attendance": appt.attendance,
                "reason": appt.reason,
                "doctor_name": appt.doctor.user.full_name if appt.doctor else None,
            }
        )

    missed_visits = []
    for appt in appointments.filter(
        Q(status=AppointmentStatus.NO_SHOW) | Q(attendance=AttendanceStatus.ABSENT)
    ).order_by("-scheduled_at")[:4]:
        missed_visits.append(
            {
                "id": str(appt.id),
                "scheduled_at": appt.scheduled_at.isoformat(),
                "status": appt.status,
                "attendance": appt.attendance,
                "reason": appt.reason,
            }
        )

    treatments = PatientTreatment.objects.filter(patient=patient)
    treatment_summary = {
        "total": treatments.count(),
        "active": treatments.filter(status__in=[TreatmentStatus.ACTIVE, TreatmentStatus.IN_PROGRESS]).count(),
        "completed": treatments.filter(status=TreatmentStatus.COMPLETED).count(),
        "on_hold": treatments.filter(status=TreatmentStatus.ON_HOLD).count(),
        "cancelled": treatments.filter(status=TreatmentStatus.CANCELLED).count(),
        "avg_progress": round(float(treatments.aggregate(avg=Avg("progress_percent"))["avg"] or 0), 1),
    }

    notifications = Notification.objects.filter(user=patient.user)
    notif_total = notifications.count()
    notif_read = notifications.filter(is_read=True).count()
    comms = {
        "sent": notif_total,
        "read": notif_read,
        "read_rate": round((notif_read / notif_total * 100), 1) if notif_total else 0,
    }

    messages = AIGeneratedMessage.objects.filter(patient=patient).order_by("-created_at")[:6]
    interventions = [
        {
            "id": str(message.id),
            "message_type": message.message_type,
            "delivery_status": message.delivery_status,
            "created_at": message.created_at.isoformat(),
        }
        for message in messages
    ]

    prediction_slice = list(
        AIPrediction.objects.filter(patient=patient).order_by("-created_at")[:2]
    )
    latest = prediction_slice[0] if prediction_slice else None
    previous = prediction_slice[1] if len(prediction_slice) > 1 else None
    trend = "stable"
    if latest and previous:
        delta = latest.probability - previous.probability
        if delta >= 0.05:
            trend = "rising"
        elif delta <= -0.05:
            trend = "falling"

    features = build_patient_features(patient, now=now)
    adherence_score = _adherence_score(features)

    milestones = {
        "first_visit": appointments.order_by("scheduled_at").values_list("scheduled_at", flat=True).first(),
        "latest_visit": appointments.order_by("-scheduled_at").values_list("scheduled_at", flat=True).first(),
        "next_visit": appointments.filter(scheduled_at__gte=now)
        .order_by("scheduled_at")
        .values_list("scheduled_at", flat=True)
        .first(),
        "treatment_started": treatments.filter(started_at__isnull=False)
        .order_by("started_at")
        .values_list("started_at", flat=True)
        .first(),
        "treatment_completed": treatments.filter(completed_at__isnull=False)
        .order_by("-completed_at")
        .values_list("completed_at", flat=True)
        .first(),
    }

    return {
        "adherence_score": adherence_score,
        "adherence_stage": _adherence_stage(adherence_score),
        "appointment_summary": {
            "total": total_appts,
            "completed": completed_appts,
            "missed": missed_appts,
            "cancelled": cancelled_appts,
            "upcoming": upcoming_appts,
        },
        "treatment_summary": treatment_summary,
        "communication_engagement": comms,
        "risk_summary": {
            "risk_level": latest.risk_level if latest else None,
            "risk_score": round(latest.probability * 100, 1) if latest else None,
            "trend": trend,
        },
        "milestones": {
            key: value.isoformat() if value else None for key, value in milestones.items()
        },
        "recent_appointments": recent_appointments,
        "missed_visits": missed_visits,
        "interventions": interventions,
        "timeline": build_patient_timeline(patient, days=days),
    }
