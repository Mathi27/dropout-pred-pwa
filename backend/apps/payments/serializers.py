from rest_framework import serializers

from apps.payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    patient_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "patient",
            "patient_id",
            "amount",
            "status",
            "payment_date",
            "method",
            "reference",
            "description",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "patient")

    def create(self, validated_data):
        from apps.patients.models import Patient

        patient_id = validated_data.pop("patient_id")
        validated_data["patient"] = Patient.objects.get(pk=patient_id)
        return super().create(validated_data)
