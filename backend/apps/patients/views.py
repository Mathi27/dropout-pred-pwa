from rest_framework import filters as drf_filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsAdmin, IsDoctorOrAdmin, IsPatient, IsStaffRole
from apps.core.querysets import get_patient_profile
from apps.core.viewsets import SoftDeleteModelViewSet
from apps.patients.filters import PatientFilter
from apps.patients.serializers import PatientSerializer
from apps.patients.services import get_patient_risk_score, get_patients_queryset


class PatientViewSet(SoftDeleteModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsStaffRole]
    filterset_class = PatientFilter
    filter_backends = [drf_filters.SearchFilter, drf_filters.OrderingFilter]
    search_fields = ["user__first_name", "user__last_name", "user__email"]
    ordering_fields = ["created_at", "user__last_name"]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.action == "me":
            return [IsAuthenticated(), IsPatient()]
        if self.action in ("list", "retrieve", "risk_sorted"):
            return [IsAuthenticated(), IsStaffRole()]
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsAdmin()]
        return super().get_permissions()

    @action(detail=False, methods=["get"])
    def me(self, request):
        profile = get_patient_profile(request.user)
        if not profile:
            return Response({"detail": "Patient profile not found."}, status=404)
        return Response(PatientSerializer(profile).data)

    def get_queryset(self):
        qs = get_patients_queryset(self.request.user)
        if self.action == "risk_sorted":
            return qs
        return qs

    @action(detail=False, methods=["get"], url_path="risk-sorted")
    def risk_sorted(self, request):
        patients = list(self.filter_queryset(self.get_queryset()))
        patients.sort(key=lambda p: get_patient_risk_score(p), reverse=True)
        page = self.paginate_queryset(patients)
        serializer = self.get_serializer(page or patients, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)
