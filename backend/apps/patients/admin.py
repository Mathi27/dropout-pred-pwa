from django.contrib import admin

from apps.patients.models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("user", "gender", "created_at", "is_deleted")
    search_fields = ("user__email", "user__first_name", "user__last_name")
