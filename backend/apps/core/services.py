from typing import Any

from django.contrib.auth import get_user_model

User = get_user_model()


def create_audit_log(
    *,
    actor: User | None,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    from apps.audit_logs.models import AuditLog

    AuditLog.objects.create(
        actor=actor,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata=metadata or {},
    )
