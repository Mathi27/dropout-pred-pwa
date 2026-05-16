from django.conf import settings
from django.db import models

from apps.core.models import SoftDeleteModel


class Receptionist(SoftDeleteModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="receptionist_profile",
    )
    desk_number = models.CharField(max_length=20, blank=True)
    shift = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = "receptionists"
        ordering = ["-created_at"]

    def __str__(self):
        return self.user.full_name
