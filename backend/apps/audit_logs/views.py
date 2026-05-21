from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.audit_logs.models import AuditLog
from apps.audit_logs.serializers import AuditLogSerializer
from apps.core.permissions import IsAdmin


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = AuditLog.objects.select_related("actor")
    filterset_fields = ["action", "resource_type", "actor"]
    ordering = ["-created_at"]
