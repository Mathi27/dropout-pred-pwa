from apps.ai_interventions.models import AIGeneratedMessage, InterventionLog


def get_patient_messages(patient, limit=30):
    return AIGeneratedMessage.objects.filter(patient=patient).order_by("-created_at")[:limit]


def get_intervention_logs(patient=None, limit=50):
    qs = InterventionLog.objects.all()
    if patient is not None:
        qs = qs.filter(patient=patient)
    return qs.order_by("-created_at")[:limit]
