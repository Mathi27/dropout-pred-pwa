from apps.ai_interventions.models import MessageType


def recommend_message_type(context: dict) -> str:
    missed_visits = context.get("missed_visits", 0)
    consecutive_misses = context.get("consecutive_misses", 0)
    upcoming = context.get("upcoming_appointment")
    days_since_last_visit = context.get("features", {}).get("days_since_last_visit", 0)

    if consecutive_misses >= 2 or missed_visits >= 3:
        return MessageType.MISSED_FOLLOWUP
    if days_since_last_visit >= 45:
        return MessageType.TREATMENT_ENCOURAGEMENT
    if upcoming:
        return MessageType.APPOINTMENT_REMINDER
    if missed_visits:
        return MessageType.MOTIVATIONAL
    return MessageType.EDUCATIONAL
