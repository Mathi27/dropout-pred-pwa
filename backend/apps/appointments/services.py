from django.utils import timezone

from apps.appointments.models import Appointment, AppointmentStatus, AttendanceStatus
from apps.core.querysets import filter_appointments_for_user
from apps.core.services import create_audit_log


def get_appointments_queryset(user):
    return filter_appointments_for_user(
        Appointment.objects.select_related("patient__user", "doctor__user"),
        user,
    )


def mark_attendance(*, appointment: Appointment, attendance: str, user) -> Appointment:
    appointment.attendance = attendance
    if attendance == AttendanceStatus.PRESENT:
        appointment.status = AppointmentStatus.COMPLETED
    elif attendance == AttendanceStatus.ABSENT:
        appointment.status = AppointmentStatus.NO_SHOW
    appointment.save()
    create_audit_log(
        actor=user,
        action="appointment.attendance_marked",
        resource_type="appointment",
        resource_id=str(appointment.id),
        metadata={"attendance": attendance},
    )
    return appointment


def reschedule_appointment(*, appointment: Appointment, new_datetime, user) -> Appointment:
    new_appt = Appointment.objects.create(
        patient=appointment.patient,
        doctor=appointment.doctor,
        scheduled_at=new_datetime,
        duration_minutes=appointment.duration_minutes,
        status=AppointmentStatus.SCHEDULED,
        reason=appointment.reason,
        rescheduled_from=appointment,
    )
    appointment.status = AppointmentStatus.RESCHEDULED
    appointment.save(update_fields=["status", "updated_at"])
    create_audit_log(
        actor=user,
        action="appointment.rescheduled",
        resource_type="appointment",
        resource_id=str(new_appt.id),
        metadata={"from": str(appointment.id)},
    )
    return new_appt
