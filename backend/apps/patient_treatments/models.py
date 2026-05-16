from django.db import models

from apps.core.models import SoftDeleteModel


class TreatmentStatus(models.TextChoices):
    PLANNED = "planned", "Planned"
    ACTIVE = "active", "Active"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    ON_HOLD = "on_hold", "On Hold"


class PatientTreatment(SoftDeleteModel):
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="patient_treatments",
    )
    treatment = models.ForeignKey(
        "treatments.Treatment",
        on_delete=models.PROTECT,
        related_name="patient_treatments",
    )
    doctor = models.ForeignKey(
        "doctors.Doctor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patient_treatments",
    )
    status = models.CharField(
        max_length=20,
        choices=TreatmentStatus.choices,
        default=TreatmentStatus.PLANNED,
        db_index=True,
    )
    progress_percent = models.PositiveSmallIntegerField(default=0)
    started_at = models.DateField(null=True, blank=True)
    completed_at = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "patient_treatments"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["patient", "status"]),
            models.Index(fields=["doctor", "status"]),
        ]

    def __str__(self):
        return f"{self.patient} — {self.treatment}"
