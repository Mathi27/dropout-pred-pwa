import hashlib

from django.contrib.auth import get_user_model
from django.db import transaction

from apps.core.querysets import filter_patients_for_user
from apps.core.services import create_audit_log
from apps.patients.models import Patient
from apps.users.models import UserRole

User = get_user_model()


def get_patients_queryset(user):
    return filter_patients_for_user(Patient.objects.select_related("user"), user)


def dummy_risk_score(patient_id) -> float:
    """Placeholder risk score until ML Phase 4."""
    digest = hashlib.md5(str(patient_id).encode()).hexdigest()
    return round(int(digest[:4], 16) / 65535 * 100, 1)


@transaction.atomic
def create_patient_profile(*, user: User, **profile_data) -> Patient:
    if user.role != UserRole.PATIENT:
        raise ValueError("User must have patient role.")
    patient, created = Patient.objects.get_or_create(user=user, defaults=profile_data)
    if not created and profile_data:
        for key, value in profile_data.items():
            setattr(patient, key, value)
        patient.save()
    return patient
