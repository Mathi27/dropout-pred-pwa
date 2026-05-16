from django.conf import settings
from django.db import models

from apps.core.models import SoftDeleteModel


class Gender(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    OTHER = "other", "Other"
    PREFER_NOT = "prefer_not", "Prefer not to say"


class Patient(SoftDeleteModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_profile",
    )
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=Gender.choices, blank=True)
    address = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=150, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    medical_notes = models.TextField(blank=True)
    blood_group = models.CharField(max_length=10, blank=True)

    class Meta:
        db_table = "patients"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_deleted", "created_at"]),
        ]

    def __str__(self):
        return self.user.full_name
