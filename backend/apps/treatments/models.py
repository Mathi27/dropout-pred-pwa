from django.db import models

from apps.core.models import SoftDeleteModel


class TreatmentCategory(models.TextChoices):
    ORTHODONTIC = "orthodontic", "Orthodontic"
    RESTORATIVE = "restorative", "Restorative"
    PREVENTIVE = "preventive", "Preventive"
    SURGICAL = "surgical", "Surgical"
    OTHER = "other", "Other"


class Treatment(SoftDeleteModel):
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=30,
        choices=TreatmentCategory.choices,
        default=TreatmentCategory.OTHER,
    )
    duration_weeks = models.PositiveIntegerField(default=12)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "treatments"
        ordering = ["name"]

    def __str__(self):
        return self.name
