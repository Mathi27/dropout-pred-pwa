import random

from django.utils import timezone

from apps.ai_interventions.models import (
    AIGeneratedMessage,
    DeliveryStatus,
    DeliveryTracking,
    InterventionAction,
    InterventionLog,
    InterventionOutcome,
)


def _delivery_outcome(rng: random.Random, base_success: float) -> str:
    return DeliveryStatus.DELIVERED if rng.random() < base_success else DeliveryStatus.FAILED


def simulate_delivery(*, message: AIGeneratedMessage, actor=None, channel="in_app") -> DeliveryTracking:
    rng = random.Random(str(message.id))
    base_success = 0.85 if message.confidence_score >= 0.65 else 0.7
    outcome = _delivery_outcome(rng, base_success)

    tracking = DeliveryTracking.objects.create(
        message=message,
        channel=channel,
        status=outcome,
        attempt=1,
        last_attempt_at=timezone.now(),
        delivered_at=timezone.now() if outcome == DeliveryStatus.DELIVERED else None,
        language=message.language,
        metadata={"confidence": message.confidence_score},
        error_message="Delivery failed" if outcome == DeliveryStatus.FAILED else "",
    )

    message.delivery_status = outcome
    message.save(update_fields=["delivery_status", "updated_at"])

    InterventionLog.objects.create(
        patient=message.patient,
        message=message,
        actor=actor,
        action=InterventionAction.SENT,
        status=InterventionOutcome.SUCCESS if outcome == DeliveryStatus.DELIVERED else InterventionOutcome.FAILED,
        metadata={"channel": channel, "delivery_status": outcome},
    )

    return tracking


def retry_delivery(*, message: AIGeneratedMessage, actor=None, channel="in_app") -> DeliveryTracking:
    last_attempt = message.deliveries.order_by("-attempt").first()
    attempt = (last_attempt.attempt + 1) if last_attempt else 1
    rng = random.Random(f"{message.id}:{attempt}")
    base_success = 0.9 if attempt > 1 else 0.75
    outcome = _delivery_outcome(rng, base_success)

    tracking = DeliveryTracking.objects.create(
        message=message,
        channel=channel,
        status=outcome,
        attempt=attempt,
        last_attempt_at=timezone.now(),
        delivered_at=timezone.now() if outcome == DeliveryStatus.DELIVERED else None,
        language=message.language,
        metadata={"confidence": message.confidence_score, "retry": True},
        error_message="Delivery failed" if outcome == DeliveryStatus.FAILED else "",
    )

    message.delivery_status = outcome
    message.save(update_fields=["delivery_status", "updated_at"])

    InterventionLog.objects.create(
        patient=message.patient,
        message=message,
        actor=actor,
        action=InterventionAction.RETRY,
        status=InterventionOutcome.SUCCESS if outcome == DeliveryStatus.DELIVERED else InterventionOutcome.FAILED,
        metadata={"channel": channel, "delivery_status": outcome, "attempt": attempt},
    )

    return tracking
