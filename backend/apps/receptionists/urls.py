from rest_framework.routers import DefaultRouter

from apps.receptionists.views import ReceptionistViewSet

router = DefaultRouter()
router.register(r"receptionists", ReceptionistViewSet, basename="receptionists")

urlpatterns = router.urls
