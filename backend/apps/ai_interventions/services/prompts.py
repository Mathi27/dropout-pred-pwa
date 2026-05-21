from apps.ai_interventions.models import MessageType


def build_prompt(*, patient_name: str, context: dict, message_type: str, language: str, clinic_name: str) -> str:
    missed = context.get("missed_visits", 0)
    consecutive = context.get("consecutive_misses", 0)
    treatment = context.get("treatment_name", "your treatment plan")
    doctor = context.get("doctor_name", "your care team")
    stage = context.get("treatment_stage", "active")

    return (
        f"Create a short, empathetic {message_type} message in {language}. "
        f"Patient name: {patient_name}. Treatment: {treatment}. Stage: {stage}. "
        f"Missed visits: {missed}. Consecutive misses: {consecutive}. "
        f"Doctor name: {doctor}. Clinic name: {clinic_name}. "
        "Avoid fear tactics and do not mention dropout risk. Keep it professional and human."
    )
