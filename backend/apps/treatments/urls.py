from rest_framework.routers import DefaultRouter

from apps.treatments.views import TreatmentViewSet

router = DefaultRouter()
router.register(r"treatments", TreatmentViewSet, basename="treatments")

urlpatterns = router.urls
