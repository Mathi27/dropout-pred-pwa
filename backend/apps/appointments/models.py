from django.db import models

from apps.core.models import SoftDeleteModel


class AppointmentStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    CONFIRMED = "confirmed", "Confirmed"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    NO_SHOW = "no_show", "No Show"
    RESCHEDULED = "rescheduled", "Rescheduled"


class AttendanceStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PRESENT = "present", "Present"
    ABSENT = "absent", "Absent"


class Appointment(SoftDeleteModel):
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    doctor = models.ForeignKey(
        "doctors.Doctor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments",
    )
    scheduled_at = models.DateTimeField(db_index=True)
    duration_minutes = models.PositiveSmallIntegerField(default=30)
    status = models.CharField(
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.SCHEDULED,
        db_index=True,
    )
    attendance = models.CharField(
        max_length=20,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PENDING,
        db_index=True,
    )
    reason = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    rescheduled_from = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rescheduled_to",
    )

    class Meta:
        db_table = "appointments"
        ordering = ["scheduled_at"]
        indexes = [
            models.Index(fields=["scheduled_at", "status"]),
            models.Index(fields=["doctor", "scheduled_at"]),
            models.Index(fields=["patient", "scheduled_at"]),
        ]

    def __str__(self):
        return f"{self.patient} @ {self.scheduled_at:%Y-%m-%d %H:%M}"
