"""Admin analytics aggregates (Phase 2)."""

from collections import Counter, defaultdict
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone

from apps.ai_interventions.models import AIGeneratedMessage, DeliveryStatus, DeliveryTracking
from apps.ai_predictions.models import AIPrediction, RiskLevel
from apps.appointments.models import Appointment, AppointmentStatus
from apps.doctors.models import Doctor
from apps.notifications.models import Notification
from apps.patient_treatments.models import PatientTreatment, TreatmentStatus
from apps.patients.models import Patient
from apps.payments.models import Payment, PaymentStatus
from apps.users.models import User, UserRole

ADMIN_ANALYTICS_CACHE_TTL = getattr(settings, "ADMIN_ANALYTICS_CACHE_TTL", 300)
ADMIN_ANALYTICS_CACHE_KEY = "admin:analytics:overview:v1"


def get_admin_analytics() -> dict:
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    appointments = Appointment.objects.all()
    total_appointments = appointments.count()
    today_appointments = appointments.filter(scheduled_at__date=today).count()
    completed = appointments.filter(status=AppointmentStatus.COMPLETED).count()
    completion_rate = round((completed / total_appointments * 100), 1) if total_appointments else 0

    appointment_trends = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        appointment_trends.append(
            {
                "date": day.isoformat(),
                "scheduled": appointments.filter(scheduled_at__date=day).count(),
                "completed": appointments.filter(
                    scheduled_at__date=day, status=AppointmentStatus.COMPLETED
                ).count(),
            }
        )

    notifications = Notification.objects.all()
    notification_metrics = {
        "total": notifications.count(),
        "unread": notifications.filter(is_read=False).count(),
        "read": notifications.filter(is_read=True).count(),
        "by_type": list(
            notifications.values("notification_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        ),
    }

    total_treatments = PatientTreatment.objects.count()
    treatments_active = PatientTreatment.objects.filter(
        status__in=[TreatmentStatus.ACTIVE, TreatmentStatus.IN_PROGRESS]
    ).count()
    treatments_completed = PatientTreatment.objects.filter(status=TreatmentStatus.COMPLETED).count()
    treatments_on_hold = PatientTreatment.objects.filter(status=TreatmentStatus.ON_HOLD).count()
    treatments_cancelled = PatientTreatment.objects.filter(status=TreatmentStatus.CANCELLED).count()

    attendance_present = appointments.filter(
        Q(attendance="present") | Q(status=AppointmentStatus.COMPLETED)
    ).count()
    attendance_absent = appointments.filter(
        Q(attendance="absent") | Q(status=AppointmentStatus.NO_SHOW)
    ).count()
    attendance_rate = round((attendance_present / total_appointments * 100), 1) if total_appointments else 0

    payments_total = Payment.objects.count()
    payments_paid = Payment.objects.filter(status=PaymentStatus.PAID).count()
    payment_rate = round((payments_paid / payments_total * 100), 1) if payments_total else 0
    notification_read_rate = (
        round((notification_metrics["read"] / notification_metrics["total"] * 100), 1)
        if notification_metrics["total"]
        else 0
    )

    latest_predictions = list(
        AIPrediction.objects.order_by("patient_id", "-created_at").distinct("patient_id")
    )
    risk_by_patient = {}
    risk_counts = {"low": 0, "medium": 0, "high": 0}
    for prediction in latest_predictions:
        risk_by_patient[prediction.patient_id] = prediction.risk_level
        risk_counts[prediction.risk_level] += 1

    current_since = today - timedelta(days=7)
    previous_since = today - timedelta(days=14)
    current_preds = AIPrediction.objects.filter(created_at__date__gte=current_since)
    previous_preds = AIPrediction.objects.filter(
        created_at__date__gte=previous_since,
        created_at__date__lt=current_since,
    )
    current_total = current_preds.count()
    previous_total = previous_preds.count()
    current_high = current_preds.filter(risk_level=RiskLevel.HIGH).count()
    previous_high = previous_preds.filter(risk_level=RiskLevel.HIGH).count()
    current_share = current_high / current_total if current_total else 0
    previous_share = previous_high / previous_total if previous_total else 0

    messages = AIGeneratedMessage.objects.filter(created_at__gte=(timezone.now() - timedelta(days=30)))
    deliveries = DeliveryTracking.objects.filter(created_at__gte=(timezone.now() - timedelta(days=30)))
    delivery_total = deliveries.count()
    delivered = deliveries.filter(status=DeliveryStatus.DELIVERED).count()
    retry_rate = (
        round((deliveries.filter(attempt__gt=1).count() / delivery_total) * 100, 1)
        if delivery_total
        else 0
    )
    delivery_success_rate = round((delivered / delivery_total) * 100, 1) if delivery_total else 0

    impact = {"improved": 0, "worsened": 0, "stable": 0}
    impacted_patients = list(messages.values_list("patient_id", flat=True).distinct())
    if impacted_patients:
        history = AIPrediction.objects.filter(patient_id__in=impacted_patients).order_by(
            "patient_id",
            "-created_at",
        )
        grouped: dict = defaultdict(list)
        for prediction in history:
            if len(grouped[prediction.patient_id]) < 2:
                grouped[prediction.patient_id].append(prediction)
        for preds in grouped.values():
            if len(preds) < 2:
                continue
            delta = preds[0].probability - preds[1].probability
            if delta <= -0.05:
                impact["improved"] += 1
            elif delta >= 0.05:
                impact["worsened"] += 1
            else:
                impact["stable"] += 1

    category_counts = defaultdict(lambda: {"low": 0, "medium": 0, "high": 0})
    patient_categories = defaultdict(Counter)
    for treatment in PatientTreatment.objects.select_related("treatment").all():
        patient_categories[treatment.patient_id][treatment.treatment.category] += 1
    for patient_id, counter in patient_categories.items():
        if not counter:
            continue
        top_category = counter.most_common(1)[0][0]
        risk = risk_by_patient.get(patient_id)
        if not risk:
            continue
        category_counts[top_category][risk] += 1
    cohort_comparison = [
        {"category": category, **counts}
        for category, counts in sorted(category_counts.items(), key=lambda item: item[0])
    ]

    doctor_performance = []
    for doctor in Doctor.objects.select_related("user"):
        doctor_appointments = Appointment.objects.filter(doctor=doctor)
        doctor_total = doctor_appointments.count()
        doctor_completed = doctor_appointments.filter(status=AppointmentStatus.COMPLETED).count()
        doctor_patients = Patient.objects.filter(
            Q(appointments__doctor=doctor) | Q(patient_treatments__doctor=doctor)
        ).distinct()
        doctor_high_risk = sum(
            1 for patient_id in doctor_patients.values_list("id", flat=True)
            if risk_by_patient.get(patient_id) == RiskLevel.HIGH
        )
        doctor_performance.append(
            {
                "doctor_id": str(doctor.id),
                "doctor_name": doctor.user.full_name,
                "appointments_total": doctor_total,
                "appointments_completed": doctor_completed,
                "completion_rate": round((doctor_completed / doctor_total * 100), 1)
                if doctor_total
                else 0,
                "patients_seen": doctor_patients.count(),
                "high_risk_patients": doctor_high_risk,
            }
        )

    return {
        "kpis": {
            "total_patients": Patient.objects.count(),
            "total_users": User.objects.filter(is_active=True).count(),
            "appointments_today": today_appointments,
            "completion_rate": completion_rate,
            "active_treatments": treatments_active,
            "completed_treatments": treatments_completed,
            "revenue_month": float(
                Payment.objects.filter(
                    payment_date__gte=month_ago,
                    status=PaymentStatus.PAID,
                ).aggregate(total=Sum("amount"))["total"]
                or 0
            ),
        },
        "appointment_trends": appointment_trends,
        "notification_metrics": notification_metrics,
        "users_by_role": list(
            User.objects.filter(is_active=True)
            .values("role")
            .annotate(count=Count("id"))
            .order_by("role")
        ),
        "attendance_heatmap": _attendance_heatmap(appointments, week_ago, today),
        "adherence_kpis": {
            "attendance_rate": attendance_rate,
            "miss_rate": round((attendance_absent / total_appointments * 100), 1)
            if total_appointments
            else 0,
            "treatment_completion_rate": round((treatments_completed / total_treatments * 100), 1)
            if total_treatments
            else 0,
            "payment_on_time_rate": payment_rate,
            "notification_read_rate": notification_read_rate,
        },
        "dropout_metrics": {
            "high_risk_share": round(current_share * 100, 1),
            "previous_high_risk_share": round(previous_share * 100, 1),
            "share_delta": round((current_share - previous_share) * 100, 1),
            "current_total": current_total,
            "previous_total": previous_total,
        },
        "intervention_success": {
            "messages_sent": messages.count(),
            "delivery_success_rate": delivery_success_rate,
            "retry_rate": retry_rate,
            "impact": impact,
        },
        "communication_effectiveness": {
            "notification_read_rate": notification_read_rate,
            "notification_by_type": notification_metrics["by_type"],
        },
        "treatment_funnel": {
            "total": total_treatments,
            "active": treatments_active,
            "on_hold": treatments_on_hold,
            "completed": treatments_completed,
            "cancelled": treatments_cancelled,
        },
        "risk_segmentation": risk_counts,
        "cohort_comparison": cohort_comparison,
        "doctor_performance": doctor_performance,
    }


def get_doctor_analytics(doctor) -> dict:
    from apps.appointments.models import Appointment

    qs = Appointment.objects.filter(doctor=doctor)
    total = qs.count()
    completed = qs.filter(status=AppointmentStatus.COMPLETED).count()
    patients_qs = Patient.objects.filter(
        Q(patient_treatments__doctor=doctor) | Q(appointments__doctor=doctor)
    ).distinct()
    latest_predictions = (
        AIPrediction.objects.filter(patient__in=patients_qs)
        .order_by("patient_id", "-created_at")
        .distinct("patient_id")
    )
    high_risk = latest_predictions.filter(risk_level=RiskLevel.HIGH).count()
    return {
        "appointments_total": total,
        "appointments_completed": completed,
        "completion_rate": round((completed / total * 100), 1) if total else 0,
        "patients_assigned": patients_qs.count(),
        "high_risk_patients": high_risk,
    }


def _attendance_heatmap(appointments, start_date, end_date) -> list[dict]:
    rows = []
    current = start_date
    while current <= end_date:
        day_qs = appointments.filter(scheduled_at__date=current)
        rows.append(
            {
                "date": current.isoformat(),
                "present": day_qs.filter(attendance="present").count(),
                "absent": day_qs.filter(attendance="absent").count(),
                "pending": day_qs.filter(attendance="pending").count(),
            }
        )
        current += timedelta(days=1)
    return rows


def get_admin_analytics_cached() -> dict:
    cached = cache.get(ADMIN_ANALYTICS_CACHE_KEY)
    if cached is not None:
        return cached
    payload = get_admin_analytics()
    cache.set(ADMIN_ANALYTICS_CACHE_KEY, payload, ADMIN_ANALYTICS_CACHE_TTL)
    return payload


def refresh_admin_analytics_cache() -> dict:
    payload = get_admin_analytics()
    cache.set(ADMIN_ANALYTICS_CACHE_KEY, payload, ADMIN_ANALYTICS_CACHE_TTL)
    return payload
