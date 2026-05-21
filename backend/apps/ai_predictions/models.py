from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel


class ModelType(models.TextChoices):
    LOGISTIC_REGRESSION = "logistic_regression", "Logistic Regression"
    RANDOM_FOREST = "random_forest", "Random Forest"
    XGBOOST = "xgboost", "XGBoost"


class RiskLevel(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"


class PredictionStatus(models.TextChoices):
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"


class ModelVersion(TimeStampedModel):
    name = models.CharField(max_length=150)
    model_type = models.CharField(max_length=50, choices=ModelType.choices, db_index=True)
    is_active = models.BooleanField(default=False, db_index=True)
    trained_at = models.DateTimeField(default=timezone.now, db_index=True)
    metrics = models.JSONField(default=dict, blank=True)
    calibration = models.JSONField(default=dict, blank=True)
    feature_names = models.JSONField(default=list, blank=True)
    hyperparameters = models.JSONField(default=dict, blank=True)
    data_summary = models.JSONField(default=dict, blank=True)
    model_path = models.CharField(max_length=255)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "model_versions"
        ordering = ["-trained_at"]
        indexes = [
            models.Index(fields=["model_type", "trained_at"]),
            models.Index(fields=["is_active", "trained_at"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.model_type})"


class AIPrediction(TimeStampedModel):
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="ai_predictions",
    )
    model_version = models.ForeignKey(
        ModelVersion,
        on_delete=models.PROTECT,
        related_name="predictions",
    )
    probability = models.FloatField()
    risk_level = models.CharField(max_length=20, choices=RiskLevel.choices, db_index=True)
    features = models.JSONField(default=dict, blank=True)
    prediction_source = models.CharField(max_length=50, default="api")

    class Meta:
        db_table = "ai_predictions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["patient", "created_at"]),
            models.Index(fields=["risk_level", "created_at"]),
        ]

    def __str__(self):
        return f"{self.patient} {self.risk_level}"


class PredictionLog(TimeStampedModel):
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="prediction_logs",
    )
    model_version = models.ForeignKey(
        ModelVersion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prediction_logs",
    )
    prediction = models.ForeignKey(
        AIPrediction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs",
    )
    status = models.CharField(
        max_length=20,
        choices=PredictionStatus.choices,
        default=PredictionStatus.SUCCESS,
        db_index=True,
    )
    latency_ms = models.PositiveIntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    source = models.CharField(max_length=50, default="api")

    class Meta:
        db_table = "prediction_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["patient", "created_at"]),
        ]

    def __str__(self):
        return f"{self.patient} {self.status}"


class ShapExplanation(TimeStampedModel):
    prediction = models.OneToOneField(
        AIPrediction,
        on_delete=models.CASCADE,
        related_name="shap_explanation",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="shap_explanations",
    )
    model_version = models.ForeignKey(
        ModelVersion,
        on_delete=models.PROTECT,
        related_name="shap_explanations",
    )
    base_value = models.FloatField()
    shap_values = models.JSONField(default=dict, blank=True)
    top_features = models.JSONField(default=list, blank=True)
    feature_values = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "shap_explanations"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["patient", "created_at"]),
        ]

    def __str__(self):
        return f"{self.patient} explanation"
