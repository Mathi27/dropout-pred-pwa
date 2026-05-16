from rest_framework import filters as drf_filters
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsAdmin, IsStaffRole
from apps.core.viewsets import SoftDeleteModelViewSet
from apps.treatments.serializers import TreatmentSerializer
from apps.treatments.services import get_treatments_queryset


class TreatmentViewSet(SoftDeleteModelViewSet):
    serializer_class = TreatmentSerializer
    permission_classes = [IsAuthenticated, IsStaffRole]
    filter_backends = [drf_filters.SearchFilter, drf_filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsAdmin()]
        return super().get_permissions()

    def get_queryset(self):
        return get_treatments_queryset(self.request.user)
