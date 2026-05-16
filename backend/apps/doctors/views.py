from rest_framework import filters as drf_filters
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsAdmin, IsStaffRole
from apps.core.viewsets import SoftDeleteModelViewSet
from apps.doctors.serializers import DoctorSerializer
from apps.doctors.services import get_doctors_queryset


class DoctorViewSet(SoftDeleteModelViewSet):
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, IsStaffRole]
    filter_backends = [drf_filters.SearchFilter, drf_filters.OrderingFilter]
    search_fields = ["user__first_name", "user__last_name", "specialization"]
    ordering_fields = ["created_at", "user__last_name"]
    ordering = ["user__last_name"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsAdmin()]
        return super().get_permissions()

    def get_queryset(self):
        return get_doctors_queryset(self.request.user)
