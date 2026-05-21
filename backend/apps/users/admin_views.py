from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsAdmin
from apps.users.serializers import UserSerializer

User = get_user_model()


class AdminUserViewSet(viewsets.ModelViewSet):
    """Admin user management."""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = User.objects.all().order_by("-created_at")
    filterset_fields = ["role", "is_active"]
    search_fields = ["email", "first_name", "last_name"]
    http_method_names = ["get", "patch", "head", "options"]
