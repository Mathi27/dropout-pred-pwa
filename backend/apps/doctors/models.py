from django.conf import settings
from django.db import models

from apps.core.models import SoftDeleteModel


class Doctor(SoftDeleteModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
    )
    specialization = models.CharField(max_length=150, blank=True)
    license_number = models.CharField(max_length=50, blank=True, db_index=True)
    bio = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        db_table = "doctors"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Dr. {self.user.full_name}"
