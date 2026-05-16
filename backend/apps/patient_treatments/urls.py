from rest_framework.routers import DefaultRouter

from apps.patient_treatments.views import PatientTreatmentViewSet

router = DefaultRouter()
router.register(r"patient-treatments", PatientTreatmentViewSet, basename="patient-treatments")

urlpatterns = router.urls
