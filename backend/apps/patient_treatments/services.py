from django.utils import timezone

from apps.core.querysets import filter_by_patient_relation, get_doctor_profile, get_patient_profile
from apps.core.services import create_audit_log
from apps.patient_treatments.models import PatientTreatment, TreatmentStatus
from apps.users.models import UserRole
from apps.notifications.services import create_notification
from apps.notifications.models import NotificationType


def get_patient_treatments_queryset(user):
    qs = PatientTreatment.objects.select_related(
        "patient__user", "treatment", "doctor__user"
    )
    return filter_by_patient_relation(qs, user, patient_field="patient")


def create_patient_treatment(*, user, validated_data) -> PatientTreatment:
    pt = PatientTreatment.objects.create(**validated_data)
    create_audit_log(
        actor=user,
        action="patient_treatment.created",
        resource_type="patient_treatment",
        resource_id=str(pt.id),
    )
    try:
        if getattr(pt.patient, "user", None):
            create_notification(
                user=pt.patient.user,
                title="Treatment plan added",
                body=f"A new treatment '{pt.treatment.name}' was added to your plan.",
                notification_type=NotificationType.TREATMENT,
                actor=user,
                metadata={"treatment_id": str(pt.id)},
            )
    except Exception:
        pass
    return pt


def update_progress(*, treatment: PatientTreatment, progress: int, user) -> PatientTreatment:
    treatment.progress_percent = min(100, max(0, progress))
    if treatment.progress_percent >= 100:
        treatment.status = TreatmentStatus.COMPLETED
        treatment.completed_at = timezone.now().date()
    elif treatment.progress_percent > 0:
        treatment.status = TreatmentStatus.IN_PROGRESS
    treatment.save()
    create_audit_log(
        actor=user,
        action="patient_treatment.progress_updated",
        resource_type="patient_treatment",
        resource_id=str(treatment.id),
        metadata={"progress": treatment.progress_percent},
    )
    try:
        if getattr(treatment.patient, "user", None):
            create_notification(
                user=treatment.patient.user,
                title="Treatment progress updated",
                body=f"Progress updated to {treatment.progress_percent}% for {treatment.treatment.name}",
                notification_type=NotificationType.TREATMENT,
                actor=user,
                metadata={"treatment_id": str(treatment.id), "progress": treatment.progress_percent},
            )
    except Exception:
        pass
    return treatment
