from rest_framework import serializers

from apps.patient_treatments.models import PatientTreatment
from apps.patients.serializers import PatientSerializer
from apps.treatments.serializers import TreatmentSerializer


class PatientTreatmentSerializer(serializers.ModelSerializer):
    patient_detail = PatientSerializer(source="patient", read_only=True)
    treatment_detail = TreatmentSerializer(source="treatment", read_only=True)
    patient_id = serializers.UUIDField(write_only=True)
    treatment_id = serializers.UUIDField(write_only=True)
    doctor_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = PatientTreatment
        fields = (
            "id",
            "patient",
            "patient_id",
            "patient_detail",
            "treatment",
            "treatment_id",
            "treatment_detail",
            "doctor",
            "doctor_id",
            "status",
            "progress_percent",
            "started_at",
            "completed_at",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "patient", "treatment", "doctor")

    def create(self, validated_data):
        patient_id = validated_data.pop("patient_id")
        treatment_id = validated_data.pop("treatment_id")
        doctor_id = validated_data.pop("doctor_id", None)
        from apps.doctors.models import Doctor
        from apps.patients.models import Patient
        from apps.treatments.models import Treatment

        validated_data["patient"] = Patient.objects.get(pk=patient_id)
        validated_data["treatment"] = Treatment.objects.get(pk=treatment_id)
        if doctor_id:
            validated_data["doctor"] = Doctor.objects.get(pk=doctor_id)
        return super().create(validated_data)
