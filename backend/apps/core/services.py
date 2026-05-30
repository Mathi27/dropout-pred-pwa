from typing import Any

from django.contrib.auth import get_user_model
from django.conf import settings

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
    audit = AuditLog.objects.create(
        actor=actor,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata=metadata or {},
    )

    # enqueue realtime publish task (best-effort)
    try:
        from apps.core.tasks import publish_audit_event

        # Try to dispatch to Celery if available
        try:
            publish_audit_event.delay(audit.id)
            # In development mode, also publish synchronously so UI updates
            # immediately even if Celery workers are not running.
            if getattr(settings, "DEBUG", False):
                from apps.core.tasks import publish_audit_event_sync

                publish_audit_event_sync(audit.id)
        except Exception:
            # Fallback to synchronous publish when Celery isn't running
            from apps.core.tasks import publish_audit_event_sync

            publish_audit_event_sync(audit.id)
    except Exception:
        # If Celery or task import fails, do not block the main flow
        pass
