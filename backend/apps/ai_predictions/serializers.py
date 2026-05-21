from rest_framework import serializers

from apps.ai_predictions.models import AIPrediction, ModelVersion, PredictionLog, ShapExplanation
from apps.patients.serializers import PatientSerializer


class ModelVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelVersion
        fields = (
            "id",
            "name",
            "model_type",
            "is_active",
            "trained_at",
            "metrics",
            "calibration",
            "feature_names",
            "hyperparameters",
            "data_summary",
        )
        read_only_fields = fields


class AIPredictionSerializer(serializers.ModelSerializer):
    patient_detail = PatientSerializer(source="patient", read_only=True)
    patient_id = serializers.UUIDField(write_only=True, required=False)
    model_version = ModelVersionSerializer(read_only=True)
    risk_score = serializers.SerializerMethodField()

    class Meta:
        model = AIPrediction
        fields = (
            "id",
            "patient",
            "patient_id",
            "patient_detail",
            "probability",
            "risk_score",
            "risk_level",
            "features",
            "model_version",
            "prediction_source",
            "created_at",
        )
        read_only_fields = (
            "id",
            "patient",
            "patient_detail",
            "risk_score",
            "model_version",
            "created_at",
        )

    def get_risk_score(self, obj):
        return round(obj.probability * 100, 1)


class ShapExplanationSerializer(serializers.ModelSerializer):
    prediction_id = serializers.UUIDField(source="prediction.id", read_only=True)

    class Meta:
        model = ShapExplanation
        fields = (
            "id",
            "prediction_id",
            "patient",
            "model_version",
            "base_value",
            "shap_values",
            "top_features",
            "feature_values",
            "created_at",
        )
        read_only_fields = fields


class PredictionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionLog
        fields = (
            "id",
            "patient",
            "model_version",
            "prediction",
            "status",
            "latency_ms",
            "error_message",
            "metadata",
            "source",
            "created_at",
        )
        read_only_fields = fields
