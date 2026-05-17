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
    """Fallback risk score when no model prediction exists."""
    digest = hashlib.md5(str(patient_id).encode()).hexdigest()
    return round(int(digest[:4], 16) / 65535 * 100, 1)


def get_patient_risk_score(patient) -> float:
    from apps.ai_predictions.services.predictor import get_latest_risk_score

    score = get_latest_risk_score(patient)
    if score is None:
        return dummy_risk_score(patient.id)
    return score


def get_patient_risk_level(patient):
    from apps.ai_predictions.services.predictor import get_latest_prediction

    prediction = get_latest_prediction(patient)
    return prediction.risk_level if prediction else None


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
