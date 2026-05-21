from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from apps.ai_predictions.models import AIPrediction, RiskLevel
from apps.ai_interventions.models import AIGeneratedMessage, DeliveryStatus, DeliveryTracking
from apps.notifications.models import Notification, NotificationType
from apps.notifications.services import create_notification
from apps.users.models import User, UserRole

DEFAULT_THRESHOLD = getattr(settings, "AI_HIGH_RISK_SHARE_THRESHOLD", 0.25)
DEFAULT_WINDOW_DAYS = getattr(settings, "AI_RISK_MONITOR_DAYS", 7)
MIN_PREDICTIONS = getattr(settings, "AI_RISK_MONITOR_MIN_PREDICTIONS", 25)


def _notify_risk_threshold_breach(*, share: float, high: int, total: int, days: int) -> int:
    since = timezone.now() - timedelta(hours=24)
    if Notification.objects.filter(
        metadata__risk_threshold=True,
        created_at__gte=since,
    ).exists():
        return 0

    title = "High-risk threshold breached"
    body = f"High-risk share at {share:.1%} ({high}/{total}) over {days}d."

    admins = User.objects.filter(role=UserRole.ADMIN, is_active=True)
    created = 0
    for admin in admins:
        create_notification(
            user=admin,
            title=title,
            body=body,
            notification_type=NotificationType.SYSTEM,
            metadata={
                "risk_threshold": True,
                "share": round(share, 3),
                "high": high,
                "total": total,
                "window_days": days,
            },
        )
        created += 1
    return created


def monitor_risk_thresholds(
    *,
    days: int | None = None,
    threshold: float | None = None,
    notify: bool = True,
) -> dict:
    window = DEFAULT_WINDOW_DAYS if days is None else days
    threshold = DEFAULT_THRESHOLD if threshold is None else threshold
    since = timezone.now() - timedelta(days=window)

    predictions = AIPrediction.objects.filter(created_at__gte=since)
    total = predictions.count()
    high = predictions.filter(risk_level=RiskLevel.HIGH).count()
    share = high / total if total else 0.0
    breached = total >= MIN_PREDICTIONS and share >= threshold

    notified = 0
    if breached and notify:
        notified = _notify_risk_threshold_breach(share=share, high=high, total=total, days=window)

    return {
        "high_risk_share": round(share, 3),
        "high_risk_count": high,
        "total_predictions": total,
        "threshold": threshold,
        "breached": breached,
        "window_days": window,
        "notifications_sent": notified,
    }


def get_automation_status(*, days: int | None = None) -> dict:
    window = DEFAULT_WINDOW_DAYS if days is None else days
    now = timezone.now()
    since_day = now - timedelta(hours=24)

    last_prediction = AIPrediction.objects.order_by("-created_at").first()
    last_queue = AIGeneratedMessage.objects.order_by("-created_at").first()

    queued = AIGeneratedMessage.objects.filter(delivery_status=DeliveryStatus.QUEUED).count()
    failed = DeliveryTracking.objects.filter(status=DeliveryStatus.FAILED, created_at__gte=since_day).count()
    predictions_24h = AIPrediction.objects.filter(created_at__gte=since_day).count()

    threshold_state = monitor_risk_thresholds(days=window, notify=False)

    return {
        "predictions_last_24h": predictions_24h,
        "queue_size": queued,
        "failed_deliveries_24h": failed,
        "last_prediction_at": last_prediction.created_at.isoformat() if last_prediction else None,
        "last_queue_at": last_queue.created_at.isoformat() if last_queue else None,
        "risk_threshold": threshold_state,
    }
