from django.db import models

from apps.core.models import SoftDeleteModel


class ClinicalNote(SoftDeleteModel):
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="clinical_notes",
    )
    doctor = models.ForeignKey(
        "doctors.Doctor",
        on_delete=models.CASCADE,
        related_name="clinical_notes",
    )
    content = models.TextField()
    visit_date = models.DateField(db_index=True)
    is_private = models.BooleanField(default=False)

    class Meta:
        db_table = "clinical_notes"
        ordering = ["-visit_date", "-created_at"]
        indexes = [
            models.Index(fields=["patient", "visit_date"]),
            models.Index(fields=["doctor", "visit_date"]),
        ]

    def __str__(self):
        return f"Note for {self.patient} on {self.visit_date}"
