from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsAdmin
from apps.core.viewsets import SoftDeleteModelViewSet
from apps.payments.filters import PaymentFilter
from apps.payments.serializers import PaymentSerializer
from apps.payments.services import get_payments_queryset


class PaymentViewSet(SoftDeleteModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = PaymentFilter
    ordering = ["-payment_date"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsAdmin()]
        return super().get_permissions()

    def get_queryset(self):
        return get_payments_queryset(self.request.user)
