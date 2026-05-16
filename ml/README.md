# DentalAI ML Module (Phase 1 Stub)

Machine learning pipeline for dropout prediction. Full implementation in Phase 4.

## Planned structure

```
ml/
  data/           # Raw and processed datasets
  features/       # Feature engineering pipelines
  models/         # Serialized model artifacts (.pkl)
  training/       # Training scripts (XGBoost champion)
  inference/      # Scoring service stubs
  notebooks/      # EDA and experimentation
```

## Phase 4 deliverables

- Feature extraction from PostgreSQL (visit_miss_rate, consecutive_misses, etc.)
- XGBoost champion model with SHAP explanations
- MLflow experiment tracking
- Celery batch scoring integration
