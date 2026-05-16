from rest_framework import serializers

from apps.doctors.models import Doctor
from apps.users.serializers import UserSerializer


class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Doctor
        fields = (
            "id",
            "user",
            "full_name",
            "specialization",
            "license_number",
            "bio",
            "is_available",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
