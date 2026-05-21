from __future__ import annotations

from collections import Counter, defaultdict
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.db.models import Avg
from django.db.models.functions import TruncWeek
from django.utils import timezone

from apps.ai_predictions.models import AIPrediction
from apps.appointments.models import Appointment, AppointmentStatus, AttendanceStatus
from apps.core.querysets import filter_patients_for_user
from apps.notifications.models import Notification
from apps.patient_treatments.models import PatientTreatment
from apps.patients.models import Patient
from apps.users.models import User, UserRole

AI_ANALYTICS_CACHE_TTL = getattr(settings, "AI_ANALYTICS_CACHE_TTL", 300)


def _cache_key(user_id, days: int) -> str:
    return f"ai:analytics:overview:{user_id}:{days}"


def _latest_predictions(patients_qs):
    return (
        AIPrediction.objects.filter(patient__in=patients_qs)
        .order_by("patient_id", "-created_at")
        .distinct("patient_id")
    )


def _prediction_history(patients_qs, limit=2):
    predictions = (
        AIPrediction.objects.filter(patient__in=patients_qs)
        .order_by("patient_id", "-created_at")
        .select_related("patient")
    )
    grouped = defaultdict(list)
    for prediction in predictions:
        if len(grouped[prediction.patient_id]) < limit:
            grouped[prediction.patient_id].append(prediction)
    return grouped


def _confidence_bucket(probability: float) -> str:
    confidence = abs(probability - 0.5) * 2
    if confidence >= 0.7:
        return "high"
    if confidence >= 0.4:
        return "medium"
    return "low"


def get_ai_analytics_overview(user, days: int = 30) -> dict:
    patients_qs = filter_patients_for_user(Patient.objects.select_related("user"), user)
    since = timezone.now() - timedelta(days=days)

    latest_predictions = list(_latest_predictions(patients_qs))
    risk_distribution = {"low": 0, "medium": 0, "high": 0}
    confidence_distribution = {"low": 0, "medium": 0, "high": 0}
    risk_by_patient = {}

    for prediction in latest_predictions:
        risk_distribution[prediction.risk_level] = risk_distribution.get(prediction.risk_level, 0) + 1
        confidence_distribution[_confidence_bucket(prediction.probability)] += 1
        risk_by_patient[prediction.patient_id] = prediction.risk_level

    history = _prediction_history(patients_qs)
    trend_counts = {"rising": 0, "falling": 0, "stable": 0}
    for preds in history.values():
        if len(preds) < 2:
            continue
        delta = preds[0].probability - preds[1].probability
        if delta >= 0.05:
            trend_counts["rising"] += 1
        elif delta <= -0.05:
            trend_counts["falling"] += 1
        else:
            trend_counts["stable"] += 1

    completion_trend = list(
        PatientTreatment.objects.filter(
            patient__in=patients_qs,
            started_at__isnull=False,
            started_at__gte=(timezone.now().date() - timedelta(weeks=12)),
        )
        .annotate(week=TruncWeek("started_at"))
        .values("week")
        .annotate(avg_progress=Avg("progress_percent"))
        .order_by("week")
    )
    completion_trend_payload = [
        {
            "week": row["week"].date().isoformat(),
            "avg_progress": round(float(row["avg_progress"] or 0), 2),
        }
        for row in completion_trend
        if row["week"]
    ]

    appointments = Appointment.objects.filter(
        patient__in=patients_qs,
        scheduled_at__gte=since,
    )
    heatmap = {i: {"weekday": i, "present": 0, "absent": 0, "pending": 0} for i in range(7)}
    for appt in appointments:
        weekday = appt.scheduled_at.weekday()
        if appt.attendance == AttendanceStatus.PRESENT or appt.status == AppointmentStatus.COMPLETED:
            heatmap[weekday]["present"] += 1
        elif appt.attendance == AttendanceStatus.ABSENT or appt.status == AppointmentStatus.NO_SHOW:
            heatmap[weekday]["absent"] += 1
        else:
            heatmap[weekday]["pending"] += 1
    adherence_heatmap = [heatmap[i] for i in range(7)]

    user_to_patient = {patient.user_id: patient.id for patient in patients_qs}
    notifications = Notification.objects.filter(
        user_id__in=list(user_to_patient.keys()),
        created_at__gte=since,
    )
    notif_stats = {"low": {"sent": 0, "read": 0}, "medium": {"sent": 0, "read": 0}, "high": {"sent": 0, "read": 0}}
    for notif in notifications:
        patient_id = user_to_patient.get(notif.user_id)
        risk = risk_by_patient.get(patient_id)
        if not risk:
            continue
        notif_stats[risk]["sent"] += 1
        if notif.is_read:
            notif_stats[risk]["read"] += 1
    notification_effectiveness = {
        risk: {
            "sent": stats["sent"],
            "read": stats["read"],
            "read_rate": round(stats["read"] / stats["sent"], 3) if stats["sent"] else 0,
        }
        for risk, stats in notif_stats.items()
    }

    notified_patient_ids = {
        user_to_patient[user_id]
        for user_id in notifications.values_list("user_id", flat=True).distinct()
        if user_id in user_to_patient
    }
    intervention = {"improved": 0, "worsened": 0, "stable": 0}
    for patient_id in notified_patient_ids:
        preds = history.get(patient_id, [])
        if len(preds) < 2:
            continue
        delta = preds[0].probability - preds[1].probability
        if delta <= -0.05:
            intervention["improved"] += 1
        elif delta >= 0.05:
            intervention["worsened"] += 1
        else:
            intervention["stable"] += 1

    category_counts = defaultdict(lambda: {"low": 0, "medium": 0, "high": 0})
    treatment_rows = PatientTreatment.objects.filter(patient__in=patients_qs).select_related("treatment")
    patient_categories = defaultdict(Counter)
    for treatment in treatment_rows:
        patient_categories[treatment.patient_id][treatment.treatment.category] += 1
    for patient_id, counter in patient_categories.items():
        if not counter:
            continue
        top_category = counter.most_common(1)[0][0]
        risk = risk_by_patient.get(patient_id)
        if not risk:
            continue
        category_counts[top_category][risk] += 1
    segmentation = [
        {"category": category, **counts}
        for category, counts in sorted(category_counts.items(), key=lambda item: item[0])
    ]

    return {
        "risk_distribution": risk_distribution,
        "confidence_distribution": confidence_distribution,
        "risk_trends": trend_counts,
        "completion_trend": completion_trend_payload,
        "adherence_heatmap": adherence_heatmap,
        "notification_effectiveness": notification_effectiveness,
        "intervention_impact": intervention,
        "segmentation": segmentation,
    }


def get_ai_analytics_overview_cached(user, days: int = 30) -> dict:
    key = _cache_key(user.id, days)
    cached = cache.get(key)
    if cached is not None:
        return cached
    payload = get_ai_analytics_overview(user, days=days)
    cache.set(key, payload, AI_ANALYTICS_CACHE_TTL)
    return payload


def refresh_ai_analytics_cache(days: int = 30) -> dict:
    admins = User.objects.filter(role=UserRole.ADMIN, is_active=True)
    refreshed = 0
    for admin in admins:
        key = _cache_key(admin.id, days)
        payload = get_ai_analytics_overview(admin, days=days)
        cache.set(key, payload, AI_ANALYTICS_CACHE_TTL)
        refreshed += 1
    return {"refreshed": refreshed, "window_days": days}
