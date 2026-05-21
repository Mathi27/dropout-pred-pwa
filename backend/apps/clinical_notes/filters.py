import django_filters

from apps.clinical_notes.models import ClinicalNote


class ClinicalNoteFilter(django_filters.FilterSet):
    patient = django_filters.UUIDFilter(field_name="patient_id")
    doctor = django_filters.UUIDFilter(field_name="doctor_id")
    visit_date = django_filters.DateFilter(field_name="visit_date")
    ordering = django_filters.OrderingFilter(fields=(("visit_date", "visit_date"),))

    class Meta:
        model = ClinicalNote
        fields = ["patient", "doctor", "visit_date"]
