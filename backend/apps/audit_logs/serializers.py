from rest_framework import serializers

from apps.audit_logs.models import AuditLog
from apps.users.serializers import UserSerializer


class AuditLogSerializer(serializers.ModelSerializer):
    actor_detail = UserSerializer(source="actor", read_only=True)

    class Meta:
        model = AuditLog
        fields = (
            "id",
            "actor",
            "actor_detail",
            "action",
            "resource_type",
            "resource_id",
            "metadata",
            "ip_address",
            "created_at",
        )
        read_only_fields = fields
