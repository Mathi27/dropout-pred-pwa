from apps.ai_predictions.models import RiskLevel

RISK_THRESHOLDS = {
    "high": 0.7,
    "medium": 0.4,
}


def classify_risk(probability: float) -> str:
    if probability >= RISK_THRESHOLDS["high"]:
        return RiskLevel.HIGH
    if probability >= RISK_THRESHOLDS["medium"]:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def probability_to_score(probability: float) -> float:
    return round(probability * 100, 1)
