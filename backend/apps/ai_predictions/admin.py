from django.contrib import admin

from apps.ai_predictions.models import AIPrediction, ModelVersion, PredictionLog, ShapExplanation


@admin.register(ModelVersion)
class ModelVersionAdmin(admin.ModelAdmin):
    list_display = ("name", "model_type", "is_active", "trained_at")
    list_filter = ("model_type", "is_active")
    search_fields = ("name",)


@admin.register(AIPrediction)
class AIPredictionAdmin(admin.ModelAdmin):
    list_display = ("patient", "risk_level", "probability", "model_version", "created_at")
    list_filter = ("risk_level", "model_version")
    search_fields = ("patient__user__email", "patient__user__first_name", "patient__user__last_name")


@admin.register(ShapExplanation)
class ShapExplanationAdmin(admin.ModelAdmin):
    list_display = ("patient", "model_version", "created_at")
    search_fields = ("patient__user__email",)


@admin.register(PredictionLog)
class PredictionLogAdmin(admin.ModelAdmin):
    list_display = ("patient", "status", "source", "created_at")
    list_filter = ("status", "source")
    search_fields = ("patient__user__email",)
