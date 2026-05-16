from rest_framework import serializers

from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            "id",
            "user",
            "title",
            "body",
            "notification_type",
            "is_read",
            "read_at",
            "metadata",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "read_at", "created_at", "updated_at")
