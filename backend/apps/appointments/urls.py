from rest_framework.routers import DefaultRouter

from apps.appointments.views import AppointmentViewSet

router = DefaultRouter()
router.register(r"appointments", AppointmentViewSet, basename="appointments")

urlpatterns = router.urls
