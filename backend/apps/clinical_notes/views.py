from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsDoctorOrAdmin
from apps.core.viewsets import SoftDeleteModelViewSet
from apps.clinical_notes.filters import ClinicalNoteFilter
from apps.clinical_notes.serializers import ClinicalNoteSerializer
from apps.clinical_notes.services import get_clinical_notes_queryset


class ClinicalNoteViewSet(SoftDeleteModelViewSet):
    serializer_class = ClinicalNoteSerializer
    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]
    filterset_class = ClinicalNoteFilter
    ordering = ["-visit_date"]

    def get_queryset(self):
        return get_clinical_notes_queryset(self.request.user)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx
