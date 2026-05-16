import django_filters

from apps.notifications.models import Notification


class NotificationFilter(django_filters.FilterSet):
    is_read = django_filters.BooleanFilter(field_name="is_read")
    notification_type = django_filters.CharFilter(field_name="notification_type")
    ordering = django_filters.OrderingFilter(fields=(("created_at", "created_at"),))

    class Meta:
        model = Notification
        fields = ["is_read", "notification_type"]
