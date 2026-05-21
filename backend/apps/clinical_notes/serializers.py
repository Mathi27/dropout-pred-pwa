from rest_framework import serializers

from apps.clinical_notes.models import ClinicalNote


class ClinicalNoteSerializer(serializers.ModelSerializer):
    patient_id = serializers.UUIDField(write_only=True)
    doctor_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = ClinicalNote
        fields = (
            "id",
            "patient",
            "patient_id",
            "doctor",
            "doctor_id",
            "content",
            "visit_date",
            "is_private",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "patient", "doctor")

    def create(self, validated_data):
        from apps.doctors.models import Doctor
        from apps.patients.models import Patient

        patient_id = validated_data.pop("patient_id")
        doctor_id = validated_data.pop("doctor_id", None)
        validated_data["patient"] = Patient.objects.get(pk=patient_id)
        if doctor_id:
            validated_data["doctor"] = Doctor.objects.get(pk=doctor_id)
        elif self.context.get("request"):
            doctor = getattr(self.context["request"].user, "doctor_profile", None)
            if doctor:
                validated_data["doctor"] = doctor
        return super().create(validated_data)
