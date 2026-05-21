from datetime import timedelta

from django.db.models import Avg, Count
from django.utils import timezone

from apps.ai_interventions.models import AIGeneratedMessage, DeliveryTracking


def get_intervention_metrics():
    since = timezone.now() - timedelta(days=30)
    messages = AIGeneratedMessage.objects.filter(created_at__gte=since)
    deliveries = DeliveryTracking.objects.filter(created_at__gte=since)

    status_counts = list(
        deliveries.values("status").annotate(count=Count("id")).order_by("status")
    )
    language_counts = list(
        messages.values("language").annotate(count=Count("id")).order_by("language")
    )
    type_counts = list(
        messages.values("message_type").annotate(count=Count("id")).order_by("message_type")
    )

    totals = {
        "messages": messages.count(),
        "delivered": deliveries.filter(status="delivered").count(),
        "failed": deliveries.filter(status="failed").count(),
    }

    avg_conf = messages.aggregate(avg=Avg("confidence_score")) if messages.exists() else {"avg": 0}

    return {
        "totals": totals,
        "status_counts": status_counts,
        "language_counts": language_counts,
        "message_type_counts": type_counts,
        "avg_confidence": float(avg_conf.get("avg") or 0),
    }
