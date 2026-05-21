from django.contrib import admin

from apps.ai_interventions.models import AIGeneratedMessage, DeliveryTracking, InterventionLog


@admin.register(AIGeneratedMessage)
class AIGeneratedMessageAdmin(admin.ModelAdmin):
    list_display = ("patient", "message_type", "language", "delivery_status", "created_at")
    list_filter = ("message_type", "language", "delivery_status")
    search_fields = ("patient__user__email", "patient__user__first_name", "patient__user__last_name")


@admin.register(DeliveryTracking)
class DeliveryTrackingAdmin(admin.ModelAdmin):
    list_display = ("message", "status", "channel", "attempt", "created_at")
    list_filter = ("status", "channel")


@admin.register(InterventionLog)
class InterventionLogAdmin(admin.ModelAdmin):
    list_display = ("patient", "action", "status", "created_at")
    list_filter = ("action", "status")
