from rest_framework.routers import DefaultRouter

from apps.clinical_notes.views import ClinicalNoteViewSet

router = DefaultRouter()
router.register(r"clinical-notes", ClinicalNoteViewSet, basename="clinical-notes")

urlpatterns = router.urls
