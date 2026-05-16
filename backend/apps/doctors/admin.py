from django.contrib import admin

from apps.doctors.models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("user", "specialization", "is_available")
