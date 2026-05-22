# Research Summary

## Methodology
- Synthetic cohort generation for treatments, appointments, payments, and notifications
- Feature engineering from behavioral signals
- Supervised binary classification for dropout risk

## Feature highlights
- visit_miss_rate
- consecutive_misses
- days_since_last_visit
- treatment_completion_pct
- overdue_payment_days
- notification_response_rate
- avg_appointment_gap

## Models
- Logistic regression baseline
- Random forest
- XGBoost (primary)

## Evaluation
- AUC, precision, recall, F1
- Calibration via Brier score
- Trend monitoring and cohort analysis

## Explainability
- SHAP per-prediction explanations
- Top feature impact for clinician review

## Intervention workflow
- Risk-based message generation
- Delivery simulation and retry scheduling
- Engagement tracked through read rates

## Limitations
- Synthetic data may not reflect all clinical behaviors
- Intervention impact is simulated, not clinical outcomes
- External validation required for production research
