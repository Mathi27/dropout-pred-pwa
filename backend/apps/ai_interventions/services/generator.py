from django.conf import settings

from apps.ai_interventions.models import (
    AIGeneratedMessage,
    DeliveryStatus,
    DeliveryTracking,
    InterventionAction,
    InterventionLog,
    InterventionOutcome,
)
from apps.ai_interventions.services.context import build_patient_context
from apps.ai_interventions.services.language import resolve_language
from apps.ai_interventions.services.prompts import build_prompt
from apps.ai_interventions.services.recommendations import recommend_message_type
from apps.ai_interventions.services.templates import render_template
from apps.ai_predictions.services.predictor import get_latest_prediction
from apps.notifications.models import NotificationType
from apps.notifications.services import create_notification


def _confidence_score(context: dict) -> float:
    features = context.get("features", {})
    richness = min(
        1.0,
        (features.get("visit_progression", 0) + features.get("notification_response_rate", 0)) / 2,
    )
    stability = 1 - min(features.get("visit_miss_rate", 0), 1)
    score = 0.55 + 0.3 * richness + 0.15 * stability
    return round(min(max(score, 0.4), 0.95), 2)


def generate_message(
    *,
    patient,
    actor=None,
    message_type: str | None = None,
    language: str | None = None,
    preview: bool = False,
    channel: str = "in_app",
):
    prediction = get_latest_prediction(patient)
    risk_level = prediction.risk_level if prediction else ""
    risk_score = round(prediction.probability * 100, 1) if prediction else None

    context = build_patient_context(patient)
    message_type = message_type or recommend_message_type(context)
    lang = resolve_language(patient.user.preferred_language, language)

    clinic_name = getattr(settings, "CLINIC_NAME", "DentalAI Clinic")
    personalization = {
        "patient_name": patient.user.full_name,
        "doctor_name": context.get("doctor_name"),
        "treatment_name": context.get("treatment_name"),
        "clinic_name": clinic_name,
    }

    prompt = build_prompt(
        patient_name=patient.user.full_name,
        context=context,
        message_type=message_type,
        language=lang,
        clinic_name=clinic_name,
    )
    content, template_key = render_template(message_type, lang, personalization)
    if not content:
        content = (
            f"Hi {patient.user.full_name}, we are here to support your care journey. "
            f"Reply if you need any assistance. — {clinic_name}"
        )
        template_key = "fallback:en"

    message = AIGeneratedMessage.objects.create(
        patient=patient,
        prediction=prediction,
        created_by=actor,
        message_type=message_type,
        language=lang,
        prompt=prompt,
        content=content,
        template_key=template_key,
        confidence_score=_confidence_score(context),
        risk_level=risk_level,
        risk_score=risk_score,
        delivery_status=DeliveryStatus.PREVIEW if preview else DeliveryStatus.QUEUED,
        personalization=personalization,
        metadata={
            "context": {
                "missed_visits": context.get("missed_visits"),
                "consecutive_misses": context.get("consecutive_misses"),
                "treatment_stage": context.get("treatment_stage"),
            },
            "channel": channel,
        },
    )

    InterventionLog.objects.create(
        patient=patient,
        message=message,
        actor=actor,
        action=InterventionAction.PREVIEWED if preview else InterventionAction.GENERATED,
        status=InterventionOutcome.SUCCESS,
        metadata={"message_type": message_type, "language": lang},
    )

    if not preview:
        DeliveryTracking.objects.create(
            message=message,
            channel=channel,
            status=DeliveryStatus.QUEUED,
            attempt=0,
            language=lang,
            metadata={"queued": True},
        )
        create_notification(
            user=patient.user,
            title="Care team message",
            body=content,
            notification_type=NotificationType.REMINDER,
            actor=actor,
            metadata={"ai_message_id": str(message.id), "language": lang},
        )

    return message
