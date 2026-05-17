from rest_framework import serializers

from apps.patients.models import Patient
from apps.patients.services import get_patient_risk_level, get_patient_risk_score
from apps.users.serializers import UserSerializer


class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True, required=False)
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    risk_score = serializers.SerializerMethodField()
    risk_level = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = (
            "id",
            "user",
            "user_id",
            "full_name",
            "email",
            "date_of_birth",
            "gender",
            "address",
            "emergency_contact_name",
            "emergency_contact_phone",
            "medical_notes",
            "blood_group",
            "risk_score",
            "risk_level",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "risk_score", "risk_level")

    def get_risk_score(self, obj):
        return get_patient_risk_score(obj)

    def get_risk_level(self, obj):
        return get_patient_risk_level(obj)
