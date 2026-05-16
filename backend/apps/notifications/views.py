from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsAdmin, IsReceptionistOrAdmin
from apps.core.viewsets import SoftDeleteModelViewSet
from apps.notifications.filters import NotificationFilter
from apps.notifications.serializers import NotificationSerializer
from apps.notifications.services import (
    create_notification,
    get_notifications_queryset,
    mark_all_read,
    mark_notification_read,
)


class NotificationViewSet(SoftDeleteModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = NotificationFilter
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsReceptionistOrAdmin()]
        return super().get_permissions()

    def get_queryset(self):
        return get_notifications_queryset(self.request.user)

    def perform_create(self, serializer):
        data = serializer.validated_data
        notification = create_notification(
            user=data["user"],
            title=data["title"],
            body=data["body"],
            notification_type=data.get("notification_type", "reminder"),
            actor=self.request.user,
            metadata=data.get("metadata"),
        )
        serializer.instance = notification

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        notification = mark_notification_read(notification=self.get_object(), user=request.user)
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read_action(self, request):
        count = mark_all_read(user=request.user)
        return Response({"marked": count})

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({"count": count})
