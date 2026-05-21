from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from apps.ai_predictions.models import AIPrediction
from apps.ai_interventions.models import AIGeneratedMessage
from apps.appointments.models import Appointment
from apps.notifications.models import Notification
from apps.payments.models import Payment
from apps.patient_treatments.models import PatientTreatment


def build_patient_timeline(patient, days: int = 120) -> list[dict]:
    since = timezone.now() - timedelta(days=days)
    events: list[dict] = []

    for prediction in AIPrediction.objects.filter(patient=patient, created_at__gte=since):
        events.append(
            {
                "type": "prediction",
                "timestamp": prediction.created_at.isoformat(),
                "risk_level": prediction.risk_level,
                "probability": prediction.probability,
            }
        )

    for appointment in Appointment.objects.filter(patient=patient, scheduled_at__gte=since):
        events.append(
            {
                "type": "appointment",
                "timestamp": appointment.scheduled_at.isoformat(),
                "status": appointment.status,
                "attendance": appointment.attendance,
            }
        )

    for treatment in PatientTreatment.objects.filter(patient=patient, started_at__isnull=False).select_related("treatment"):
        if treatment.started_at and treatment.started_at >= since.date():
            events.append(
                {
                    "type": "treatment",
                    "timestamp": treatment.started_at.isoformat(),
                    "status": treatment.status,
                    "progress_percent": treatment.progress_percent,
                    "treatment_name": treatment.treatment.name,
                }
            )
        if treatment.completed_at and treatment.completed_at >= since.date():
            events.append(
                {
                    "type": "treatment",
                    "timestamp": treatment.completed_at.isoformat(),
                    "status": treatment.status,
                    "progress_percent": treatment.progress_percent,
                    "treatment_name": treatment.treatment.name,
                }
            )

    for payment in Payment.objects.filter(patient=patient, payment_date__gte=since.date()):
        events.append(
            {
                "type": "payment",
                "timestamp": payment.payment_date.isoformat(),
                "status": payment.status,
                "amount": float(payment.amount),
            }
        )

    for notification in Notification.objects.filter(user=patient.user, created_at__gte=since):
        events.append(
            {
                "type": "intervention",
                "timestamp": notification.created_at.isoformat(),
                "status": "read" if notification.is_read else "unread",
                "notification_type": notification.notification_type,
            }
        )

    for message in AIGeneratedMessage.objects.filter(patient=patient, created_at__gte=since):
        events.append(
            {
                "type": "intervention",
                "timestamp": message.created_at.isoformat(),
                "status": message.delivery_status,
                "message_type": message.message_type,
            }
        )

    events.sort(key=lambda item: item["timestamp"], reverse=True)
    return events
