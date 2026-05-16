from django.utils import timezone

from apps.core.querysets import filter_notifications_for_user
from apps.core.services import create_audit_log
from apps.notifications.models import Notification
from apps.users.models import UserRole


def get_notifications_queryset(user):
    return filter_notifications_for_user(
        Notification.objects.select_related("user"),
        user,
    )


def create_notification(*, user, title, body, notification_type, actor=None, metadata=None) -> Notification:
    notification = Notification.objects.create(
        user=user,
        title=title,
        body=body,
        notification_type=notification_type,
        metadata=metadata or {},
    )
    create_audit_log(
        actor=actor,
        action="notification.created",
        resource_type="notification",
        resource_id=str(notification.id),
    )
    return notification


def mark_notification_read(*, notification: Notification, user) -> Notification:
    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save(update_fields=["is_read", "read_at", "updated_at"])
    return notification


def mark_all_read(*, user) -> int:
    return get_notifications_queryset(user).filter(is_read=False).update(
        is_read=True, read_at=timezone.now()
    )
