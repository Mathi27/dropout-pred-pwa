from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from apps.ai_predictions.models import AIPrediction, RiskLevel
from apps.ai_predictions.services.predictor import generate_prediction
from apps.notifications.models import Notification, NotificationType
from apps.notifications.services import create_notification
from apps.patients.models import Patient
from apps.users.models import User, UserRole

DEFAULT_COOLDOWN_DAYS = getattr(settings, "AI_PREDICTION_COOLDOWN_DAYS", 1)
ESCALATION_DELTA = getattr(settings, "AI_RISK_ESCALATION_DELTA", 0.12)
ESCALATION_COOLDOWN_DAYS = getattr(settings, "AI_RISK_ESCALATION_COOLDOWN_DAYS", 7)
ESCALATION_MIN_PROB = getattr(settings, "AI_RISK_ESCALATION_MIN_PROB", 0.7)


def _latest_predictions_map(patients: list[Patient]) -> dict:
    if not patients:
        return {}
    patient_ids = [patient.id for patient in patients]
    latest = (
        AIPrediction.objects.filter(patient_id__in=patient_ids)
        .order_by("patient_id", "-created_at")
        .distinct("patient_id")
    )
    return {prediction.patient_id: prediction for prediction in latest}


def _should_escalate(previous: AIPrediction | None, current: AIPrediction) -> dict | None:
    if not previous:
        return None
    delta = current.probability - previous.probability
    crossed_high = previous.risk_level != RiskLevel.HIGH and current.risk_level == RiskLevel.HIGH
    if crossed_high:
        return {"reason": "crossed_high", "delta": round(delta, 3)}
    if current.probability >= ESCALATION_MIN_PROB and delta >= ESCALATION_DELTA:
        return {"reason": "rapid_increase", "delta": round(delta, 3)}
    return None


def _notify_risk_escalation(
    *,
    patient: Patient,
    prediction: AIPrediction,
    escalation: dict,
    actor=None,
) -> int:
    since = timezone.now() - timedelta(days=ESCALATION_COOLDOWN_DAYS)
    if Notification.objects.filter(
        metadata__risk_escalation=True,
        metadata__patient_id=str(patient.id),
        created_at__gte=since,
    ).exists():
        return 0

    score = round(prediction.probability * 100, 1)
    title = f"Risk escalation: {patient.user.full_name}"
    body = f"{patient.user.full_name} is now {prediction.risk_level} risk ({score}%)."

    admins = User.objects.filter(role=UserRole.ADMIN, is_active=True)
    created = 0
    for admin in admins:
        create_notification(
            user=admin,
            title=title,
            body=body,
            notification_type=NotificationType.SYSTEM,
            actor=actor,
            metadata={
                "risk_escalation": True,
                "patient_id": str(patient.id),
                "risk_level": prediction.risk_level,
                "risk_score": score,
                "delta": escalation.get("delta"),
                "reason": escalation.get("reason"),
            },
        )
        created += 1

    return created


def predict_all_patients(
    *,
    actor=None,
    source: str = "automation",
    min_days: int | None = None,
    max_patients: int | None = None,
) -> dict:
    min_days = DEFAULT_COOLDOWN_DAYS if min_days is None else min_days
    patients_qs = Patient.objects.select_related("user")
    if max_patients:
        patients_qs = patients_qs[:max_patients]
    patients = list(patients_qs)

    latest_map = _latest_predictions_map(patients)
    cutoff = timezone.now() - timedelta(days=min_days)

    stats = {
        "total_patients": len(patients),
        "predicted": 0,
        "skipped_recent": 0,
        "errors": 0,
        "escalations": 0,
        "error_samples": [],
    }

    for patient in patients:
        previous = latest_map.get(patient.id)
        if previous and previous.created_at >= cutoff:
            stats["skipped_recent"] += 1
            continue
        try:
            prediction = generate_prediction(patient=patient, user=actor, source=source)
            stats["predicted"] += 1
            escalation = _should_escalate(previous, prediction)
            if escalation:
                stats["escalations"] += _notify_risk_escalation(
                    patient=patient,
                    prediction=prediction,
                    escalation=escalation,
                    actor=actor,
                )
        except Exception as exc:  # pragma: no cover - defensive logging only
            stats["errors"] += 1
            if len(stats["error_samples"]) < 5:
                stats["error_samples"].append(str(exc)[:200])

    stats["ran_at"] = timezone.now().isoformat()
    return stats
