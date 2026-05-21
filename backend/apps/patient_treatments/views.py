from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsDoctorOrAdmin
from apps.core.viewsets import SoftDeleteModelViewSet
from apps.patient_treatments.filters import PatientTreatmentFilter
from apps.patient_treatments.serializers import PatientTreatmentSerializer
from apps.core.services import create_audit_log
from apps.patient_treatments.services import get_patient_treatments_queryset, update_progress


class PatientTreatmentViewSet(SoftDeleteModelViewSet):
    serializer_class = PatientTreatmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = PatientTreatmentFilter

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy", "update_progress"):
            return [IsAuthenticated(), IsDoctorOrAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return get_patient_treatments_queryset(self.request.user)

    def perform_create(self, serializer):
        pt = serializer.save()
        create_audit_log(
            actor=self.request.user,
            action="patient_treatment.created",
            resource_type="patient_treatment",
            resource_id=str(pt.id),
        )

    @action(detail=True, methods=["post"], url_path="update-progress")
    def update_progress_action(self, request, pk=None):
        progress = request.data.get("progress_percent")
        if progress is None:
            return Response({"detail": "progress_percent required"}, status=status.HTTP_400_BAD_REQUEST)
        treatment = update_progress(
            treatment=self.get_object(),
            progress=int(progress),
            user=request.user,
        )
        return Response(PatientTreatmentSerializer(treatment).data)
