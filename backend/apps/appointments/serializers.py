from rest_framework import serializers

from apps.appointments.models import Appointment
from apps.doctors.serializers import DoctorSerializer
from apps.patients.serializers import PatientSerializer


class AppointmentSerializer(serializers.ModelSerializer):
    patient_detail = PatientSerializer(source="patient", read_only=True)
    doctor_detail = DoctorSerializer(source="doctor", read_only=True)
    patient_id = serializers.UUIDField(write_only=True)
    doctor_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Appointment
        fields = (
            "id",
            "patient",
            "patient_id",
            "patient_detail",
            "doctor",
            "doctor_id",
            "doctor_detail",
            "scheduled_at",
            "duration_minutes",
            "status",
            "attendance",
            "reason",
            "notes",
            "rescheduled_from",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "patient", "doctor", "rescheduled_from")

    def create(self, validated_data):
        from apps.doctors.models import Doctor
        from apps.patients.models import Patient

        patient_id = validated_data.pop("patient_id")
        doctor_id = validated_data.pop("doctor_id", None)
        validated_data["patient"] = Patient.objects.get(pk=patient_id)
        if doctor_id:
            validated_data["doctor"] = Doctor.objects.get(pk=doctor_id)
        return super().create(validated_data)
