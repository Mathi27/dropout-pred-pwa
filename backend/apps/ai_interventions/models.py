from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class MessageType(models.TextChoices):
    APPOINTMENT_REMINDER = "appointment_reminder", "Appointment Reminder"
    MISSED_FOLLOWUP = "missed_followup", "Missed Appointment Follow-up"
    TREATMENT_ENCOURAGEMENT = "treatment_encouragement", "Treatment Continuation"
    MOTIVATIONAL = "motivational", "Motivational Reminder"
    EDUCATIONAL = "educational", "Educational Tip"


class DeliveryChannel(models.TextChoices):
    IN_APP = "in_app", "In App"
    EMAIL = "email", "Email"
    SMS = "sms", "SMS"
    WHATSAPP = "whatsapp", "WhatsApp"
    PUSH = "push", "Push Notification"


class DeliveryStatus(models.TextChoices):
    PREVIEW = "preview", "Preview"
    QUEUED = "queued", "Queued"
    SENT = "sent", "Sent"
    DELIVERED = "delivered", "Delivered"
    FAILED = "failed", "Failed"


class InterventionAction(models.TextChoices):
    PREVIEWED = "previewed", "Previewed"
    GENERATED = "generated", "Generated"
    SENT = "sent", "Sent"
    RETRY = "retry", "Retry"
    STATUS_UPDATE = "status_update", "Status Update"


class InterventionOutcome(models.TextChoices):
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"


class AIGeneratedMessage(TimeStampedModel):
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="ai_messages",
    )
    prediction = models.ForeignKey(
        "ai_predictions.AIPrediction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_messages",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_messages",
    )
    message_type = models.CharField(max_length=50, choices=MessageType.choices, db_index=True)
    language = models.CharField(max_length=10, db_index=True)
    prompt = models.TextField(blank=True)
    content = models.TextField()
    template_key = models.CharField(max_length=120, blank=True)
    provider = models.CharField(max_length=50, default="mock")
    confidence_score = models.FloatField(default=0.0)
    risk_level = models.CharField(max_length=20, blank=True)
    risk_score = models.FloatField(null=True, blank=True)
    delivery_status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PREVIEW,
        db_index=True,
    )
    personalization = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "ai_generated_messages"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["patient", "created_at"]),
            models.Index(fields=["message_type", "created_at"]),
            models.Index(fields=["delivery_status", "created_at"]),
        ]

    def __str__(self):
        return f"{self.patient} {self.message_type}"


class DeliveryTracking(TimeStampedModel):
    message = models.ForeignKey(
        AIGeneratedMessage,
        on_delete=models.CASCADE,
        related_name="deliveries",
    )
    channel = models.CharField(
        max_length=20,
        choices=DeliveryChannel.choices,
        default=DeliveryChannel.IN_APP,
    )
    status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.QUEUED,
        db_index=True,
    )
    attempt = models.PositiveIntegerField(default=1)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    language = models.CharField(max_length=10, blank=True)
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "delivery_tracking"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["channel", "created_at"]),
        ]

    def __str__(self):
        return f"{self.message_id} {self.status}"


class InterventionLog(TimeStampedModel):
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="intervention_logs",
    )
    message = models.ForeignKey(
        AIGeneratedMessage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="intervention_logs",
    )
    action = models.CharField(max_length=40, choices=InterventionAction.choices, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=InterventionOutcome.choices,
        default=InterventionOutcome.SUCCESS,
    )
    impact_score = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "intervention_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["patient", "created_at"]),
            models.Index(fields=["action", "created_at"]),
        ]

    def __str__(self):
        return f"{self.patient} {self.action}"
