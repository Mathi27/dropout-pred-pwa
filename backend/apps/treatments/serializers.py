from rest_framework import serializers

from apps.treatments.models import Treatment


class TreatmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Treatment
        fields = (
            "id",
            "name",
            "description",
            "category",
            "duration_weeks",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
