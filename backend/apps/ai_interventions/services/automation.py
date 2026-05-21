from __future__ import annotations

from collections import defaultdict
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from apps.ai_interventions.models import AIGeneratedMessage, DeliveryStatus
from apps.ai_interventions.services.delivery import retry_delivery
from apps.ai_interventions.services.generator import generate_message
from apps.ai_predictions.models import AIPrediction, RiskLevel
from apps.patients.models import Patient

QUEUE_COOLDOWN_DAYS = getattr(settings, "AI_INTERVENTION_COOLDOWN_DAYS", 7)
MAX_QUEUE_PER_RUN = getattr(settings, "AI_INTERVENTION_MAX_QUEUE", 200)
RISING_DELTA = getattr(settings, "AI_RISK_RISING_DELTA", 0.08)
MAX_RETRY_ATTEMPTS = getattr(settings, "AI_RETRY_MAX_ATTEMPTS", 3)


def _prediction_history_map(patient_ids: list) -> dict:
    if not patient_ids:
        return {}
    predictions = (
        AIPrediction.objects.filter(patient_id__in=patient_ids)
        .select_related("patient", "patient__user")
        .order_by("patient_id", "-created_at")
    )
    grouped: dict = defaultdict(list)
    for prediction in predictions:
        if len(grouped[prediction.patient_id]) < 2:
            grouped[prediction.patient_id].append(prediction)
    return grouped


def queue_interventions_for_high_risk(
    *,
    actor=None,
    source: str = "automation",
    min_days_between: int | None = None,
    max_per_run: int | None = None,
) -> dict:
    cooldown = QUEUE_COOLDOWN_DAYS if min_days_between is None else min_days_between
    max_per_run = MAX_QUEUE_PER_RUN if max_per_run is None else max_per_run
    since = timezone.now() - timedelta(days=cooldown)

    patients = list(Patient.objects.select_related("user"))
    history = _prediction_history_map([patient.id for patient in patients])

    recent_messages = set(
        AIGeneratedMessage.objects.filter(created_at__gte=since)
        .exclude(delivery_status=DeliveryStatus.PREVIEW)
        .values_list("patient_id", flat=True)
    )

    queued = 0
    skipped_recent = 0
    skipped_low = 0

    for patient in patients:
        preds = history.get(patient.id, [])
        if not preds:
            continue
        latest = preds[0]
        previous = preds[1] if len(preds) > 1 else None
        rising = False
        if previous:
            rising = (latest.probability - previous.probability) >= RISING_DELTA

        if latest.risk_level != RiskLevel.HIGH and not rising:
            skipped_low += 1
            continue
        if patient.id in recent_messages:
            skipped_recent += 1
            continue

        generate_message(
            patient=patient,
            actor=actor,
            preview=False,
            channel="in_app",
        )
        queued += 1
        if queued >= max_per_run:
            break

    return {
        "queued": queued,
        "skipped_recent": skipped_recent,
        "skipped_low_risk": skipped_low,
        "window_days": cooldown,
        "max_per_run": max_per_run,
        "source": source,
    }


def _retry_delay_minutes(attempt: int) -> int:
    if attempt <= 1:
        return 60
    if attempt == 2:
        return 6 * 60
    return 24 * 60


def process_delivery_retries(*, actor=None, max_attempts: int | None = None) -> dict:
    max_attempts = MAX_RETRY_ATTEMPTS if max_attempts is None else max_attempts
    now = timezone.now()

    messages = AIGeneratedMessage.objects.filter(delivery_status=DeliveryStatus.FAILED)
    retried = 0
    skipped_recent = 0
    exhausted = 0

    for message in messages:
        last_attempt = message.deliveries.order_by("-attempt").first()
        if not last_attempt:
            continue
        if last_attempt.attempt >= max_attempts:
            exhausted += 1
            continue
        if last_attempt.last_attempt_at:
            delay_minutes = _retry_delay_minutes(last_attempt.attempt)
            if now - last_attempt.last_attempt_at < timedelta(minutes=delay_minutes):
                skipped_recent += 1
                continue
        retry_delivery(message=message, actor=actor)
        retried += 1

    return {
        "retried": retried,
        "skipped_recent": skipped_recent,
        "exhausted": exhausted,
        "max_attempts": max_attempts,
    }
