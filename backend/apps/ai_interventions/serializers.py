from rest_framework import serializers

from apps.ai_interventions.models import AIGeneratedMessage, DeliveryTracking, InterventionLog
from apps.patients.serializers import PatientSerializer


class DeliveryTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryTracking
        fields = (
            "id",
            "status",
            "channel",
            "attempt",
            "last_attempt_at",
            "delivered_at",
            "language",
            "error_message",
            "metadata",
            "created_at",
        )
        read_only_fields = fields


class AIGeneratedMessageSerializer(serializers.ModelSerializer):
    patient_detail = PatientSerializer(source="patient", read_only=True)
    deliveries = DeliveryTrackingSerializer(many=True, read_only=True)

    class Meta:
        model = AIGeneratedMessage
        fields = (
            "id",
            "patient",
            "patient_detail",
            "prediction",
            "created_by",
            "message_type",
            "language",
            "prompt",
            "content",
            "template_key",
            "provider",
            "confidence_score",
            "risk_level",
            "risk_score",
            "delivery_status",
            "personalization",
            "metadata",
            "deliveries",
            "created_at",
        )
        read_only_fields = fields


class InterventionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterventionLog
        fields = (
            "id",
            "patient",
            "message",
            "actor",
            "action",
            "status",
            "impact_score",
            "notes",
            "metadata",
            "created_at",
        )
        read_only_fields = fields
