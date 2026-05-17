from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.users.urls")),
    path("api/v1/", include("apps.core.urls")),
    path("api/v1/", include("apps.patients.urls")),
    path("api/v1/", include("apps.doctors.urls")),
    path("api/v1/", include("apps.receptionists.urls")),
    path("api/v1/", include("apps.treatments.urls")),
    path("api/v1/", include("apps.patient_treatments.urls")),
    path("api/v1/", include("apps.appointments.urls")),
    path("api/v1/", include("apps.notifications.urls")),
    path("api/v1/", include("apps.clinical_notes.urls")),
    path("api/v1/", include("apps.payments.urls")),
    path("api/v1/", include("apps.audit_logs.urls")),
    path("api/v1/", include("apps.ai_predictions.urls")),
    path("api/v1/", include("apps.ai_interventions.urls")),
]
