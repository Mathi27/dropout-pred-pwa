"""
Mock AI Prediction Service for Demo/Testing

This module provides a mock prediction service that generates realistic
predictions without requiring actual ML model files. Useful for demos
and testing when ML models are not available.
"""

import time
import random
from datetime import timedelta

from django.utils import timezone

from apps.ai_predictions.models import (
    AIPrediction, 
    ModelVersion, 
    PredictionLog, 
    PredictionStatus, 
    RiskLevel,
    ShapExplanation
)


def get_active_model_version():
    """Get or create a mock active model version."""
    model = ModelVersion.objects.filter(is_active=True).first()
    if not model:
        model = ModelVersion.objects.create(
            name="DentalAI Mock Predictor v1.0",
            model_type="logistic_regression",
            is_active=True,
            trained_at=timezone.now(),
            metrics={
                'accuracy': 0.85,
                'precision': 0.83,
                'recall': 0.81,
                'f1_score': 0.82,
                'auc_roc': 0.88
            },
            feature_names=[
                'missed_appointments',
                'treatment_progress',
                'days_since_last_visit',
                'engagement_score',
                'payment_status',
                'age',
                'treatment_type'
            ],
            model_path="mock://predictor"
        )
    return model


def generate_mock_prediction(*, patient, user=None, source="api") -> AIPrediction:
    """
    Generate a mock prediction based on patient data patterns.
    This creates realistic predictions without requiring ML models.
    """
    start = time.monotonic()
    
    try:
        model_version = get_active_model_version()
        
        # Build features from patient data
        features = _build_mock_features(patient)
        
        # Calculate probability based on features
        probability = _calculate_mock_probability(features, patient)
        
        # Classify risk level
        risk_level = _classify_risk(probability)
        
        # Create prediction
        prediction = AIPrediction.objects.create(
            patient=patient,
            model_version=model_version,
            probability=probability,
            risk_level=risk_level,
            features=features,
            prediction_source=source,
        )
        
        # Create prediction log
        latency_ms = int((time.monotonic() - start) * 1000)
        PredictionLog.objects.create(
            patient=patient,
            model_version=model_version,
            prediction=prediction,
            status=PredictionStatus.SUCCESS,
            latency_ms=latency_ms,
            metadata={"actor": str(getattr(user, "id", "")), "mock": True},
            source=source,
        )
        
        # Generate SHAP explanation
        _create_mock_shap_explanation(prediction, patient, features)
        
        return prediction
        
    except Exception as exc:
        latency_ms = int((time.monotonic() - start) * 1000)
        PredictionLog.objects.create(
            patient=patient,
            model_version=model_version if 'model_version' in locals() else None,
            status=PredictionStatus.FAILED,
            latency_ms=latency_ms,
            error_message=str(exc),
            metadata={"actor": str(getattr(user, "id", "")), "mock": True},
            source=source,
        )
        raise


def _build_mock_features(patient):
    """Build feature dictionary from patient data."""
    from django.db.models import Avg
    from apps.appointments.models import Appointment, AppointmentStatus
    from apps.patient_treatments.models import PatientTreatment
    
    # Count missed appointments
    missed = Appointment.objects.filter(
        patient=patient,
        status__in=[AppointmentStatus.NO_SHOW, AppointmentStatus.CANCELLED]
    ).count()
    
    # Get treatment progress
    treatments = PatientTreatment.objects.filter(patient=patient)
    avg_progress = treatments.aggregate(avg=Avg('progress_percent'))['avg'] or 0
    
    # Days since last visit
    last_appt = Appointment.objects.filter(
        patient=patient,
        status=AppointmentStatus.COMPLETED
    ).order_by('-scheduled_at').first()
    days_since = (timezone.now() - last_appt.scheduled_at).days if last_appt else 90
    
    # Engagement score (mock calculation)
    engagement = max(0, 1 - (missed / max(1, Appointment.objects.filter(patient=patient).count())))
    
    return {
        'missed_appointments': missed,
        'treatment_progress': avg_progress,
        'days_since_last_visit': days_since,
        'engagement_score': round(engagement, 2),
        'payment_status': 0,  # Simplified
        'age': 30,  # Default
        'treatment_type': 1 if treatments.exists() else 0,
    }


def _calculate_mock_probability(features, patient):
    """
    Calculate mock probability based on features.
    Uses a simple weighted formula to simulate ML prediction.
    """
    # Base probability
    prob = 0.30  # Base risk
    
    # Increase risk for missed appointments
    missed = features.get('missed_appointments', 0)
    prob += missed * 0.15
    
    # Decrease risk for treatment progress
    progress = features.get('treatment_progress', 0)
    prob -= (progress / 100) * 0.20
    
    # Increase risk for days since last visit
    days = features.get('days_since_last_visit', 0)
    prob += min(days / 100, 0.20)
    
    # Decrease risk for engagement
    engagement = features.get('engagement_score', 0.5)
    prob -= engagement * 0.15
    
    # Clamp to valid range
    prob = max(0.05, min(0.95, prob))
    
    return round(prob, 4)


def _classify_risk(probability):
    """Classify risk level based on probability."""
    if probability >= 0.70:
        return RiskLevel.HIGH
    elif probability >= 0.40:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.LOW


def _create_mock_shap_explanation(prediction, patient, features):
    """Create a mock SHAP explanation for the prediction."""
    # Calculate SHAP-like values based on features
    base_value = 0.30  # Base risk
    
    shap_values = {}
    top_features = []
    
    # Missed appointments impact
    missed_impact = (features.get('missed_appointments', 0)) * 0.10
    shap_values['missed_appointments'] = round(missed_impact, 4)
    
    # Treatment progress impact (negative = reduces risk)
    progress_impact = -(features.get('treatment_progress', 0) / 100) * 0.15
    shap_values['treatment_progress'] = round(progress_impact, 4)
    
    # Days since last visit impact
    days_impact = min(features.get('days_since_last_visit', 0) / 100, 0.15)
    shap_values['days_since_last_visit'] = round(days_impact, 4)
    
    # Engagement impact (negative = reduces risk)
    engagement_impact = -(features.get('engagement_score', 0.5)) * 0.10
    shap_values['engagement_score'] = round(engagement_impact, 4)
    
    shap_values['base_value'] = base_value
    
    # Create top features list sorted by absolute impact
    for feature, value in sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True):
        if feature != 'base_value':
            top_features.append({
                'feature': feature,
                'value': features.get(feature, 0),
                'impact': value
            })
    
    ShapExplanation.objects.create(
        prediction=prediction,
        patient=patient,
        model_version=prediction.model_version,
        base_value=base_value,
        shap_values=shap_values,
        top_features=top_features[:3],  # Top 3 features
        feature_values=features,
    )


def get_latest_prediction(patient):
    """Get the latest prediction for a patient."""
    return AIPrediction.objects.filter(patient=patient).order_by('-created_at').first()


def get_latest_risk_score(patient):
    """Get the latest risk score for a patient."""
    prediction = get_latest_prediction(patient)
    if not prediction:
        return None
    return round(prediction.probability * 100, 1)