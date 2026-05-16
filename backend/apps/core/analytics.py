"""Admin analytics aggregates (Phase 2)."""

from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone

from apps.appointments.models import Appointment, AppointmentStatus
from apps.notifications.models import Notification
from apps.patient_treatments.models import PatientTreatment, TreatmentStatus
from apps.patients.models import Patient
from apps.payments.models import Payment, PaymentStatus
from apps.users.models import User, UserRole


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

    treatments_active = PatientTreatment.objects.filter(
        status__in=[TreatmentStatus.ACTIVE, TreatmentStatus.IN_PROGRESS]
    ).count()
    treatments_completed = PatientTreatment.objects.filter(status=TreatmentStatus.COMPLETED).count()

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
                ).aggregate(total=Count("amount"))["total"]
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
    }


def get_doctor_analytics(doctor) -> dict:
    from apps.appointments.models import Appointment

    qs = Appointment.objects.filter(doctor=doctor)
    total = qs.count()
    completed = qs.filter(status=AppointmentStatus.COMPLETED).count()
    return {
        "appointments_total": total,
        "appointments_completed": completed,
        "completion_rate": round((completed / total * 100), 1) if total else 0,
        "patients_assigned": Patient.objects.filter(
            Q(patient_treatments__doctor=doctor) | Q(appointments__doctor=doctor)
        ).distinct().count(),
        "high_risk_patients": 0,
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
