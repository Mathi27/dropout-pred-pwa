import django_filters

from apps.patient_treatments.models import PatientTreatment


class PatientTreatmentFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status")
    patient = django_filters.UUIDFilter(field_name="patient_id")
    doctor = django_filters.UUIDFilter(field_name="doctor_id")
    ordering = django_filters.OrderingFilter(fields=(("created_at", "created_at"), ("progress_percent", "progress")))

    class Meta:
        model = PatientTreatment
        fields = ["status", "patient", "doctor"]
