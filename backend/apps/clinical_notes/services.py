from apps.clinical_notes.models import ClinicalNote
from apps.core.querysets import filter_by_patient_relation, get_doctor_profile
from apps.users.models import UserRole


def get_clinical_notes_queryset(user):
    qs = ClinicalNote.objects.select_related("patient__user", "doctor__user")
    qs = filter_by_patient_relation(qs, user, patient_field="patient")
    if user.role == UserRole.DOCTOR:
        doctor = get_doctor_profile(user)
        if doctor:
            qs = qs.filter(doctor=doctor)
    return qs
