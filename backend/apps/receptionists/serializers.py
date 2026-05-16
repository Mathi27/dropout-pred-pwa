from rest_framework import serializers

from apps.receptionists.models import Receptionist
from apps.users.serializers import UserSerializer


class ReceptionistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Receptionist
        fields = ("id", "user", "full_name", "desk_number", "shift", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")
