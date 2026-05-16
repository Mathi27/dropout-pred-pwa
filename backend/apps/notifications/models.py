from django.conf import settings
from django.db import models

from apps.core.models import SoftDeleteModel


class NotificationType(models.TextChoices):
    APPOINTMENT = "appointment", "Appointment"
    TREATMENT = "treatment", "Treatment"
    PAYMENT = "payment", "Payment"
    REMINDER = "reminder", "Reminder"
    SYSTEM = "system", "System"
    GENERAL = "general", "General"


class Notification(SoftDeleteModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=200)
    body = models.TextField()
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL,
        db_index=True,
    )
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
        ]

    def __str__(self):
        return self.title
