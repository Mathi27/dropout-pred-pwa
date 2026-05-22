# Architecture Diagrams

## System architecture

```mermaid
graph TD
  U[Users] --> FE[Frontend (React/Vite)]
  FE --> API[Django API]
  API --> DB[(PostgreSQL)]
  API --> REDIS[(Redis)]
  API --> ML[Model Registry]
  REDIS --> CELERY[Celery Workers]
  CELERY --> API
  API --> NOTIF[Notifications]
  API --> LOGS[Audit Logs]
```

## AI workflow

```mermaid
flowchart LR
  DATA[Clinical data] --> FEAT[Feature builder]
  FEAT --> TRAIN[Model training]
  TRAIN --> MODEL[Model version]
  MODEL --> PRED[Prediction API]
  PRED --> RISK[Risk tier]
  PRED --> SHAP[Explainability]
  RISK --> ANALYTICS[AI analytics]
```

## Intervention workflow

```mermaid
flowchart LR
  RISK[High risk signal] --> GEN[Generate message]
  GEN --> QUEUE[Queue delivery]
  QUEUE --> SEND[Simulate delivery]
  SEND --> TRACK[Delivery tracking]
  TRACK --> METRICS[Intervention metrics]
```

## Automation workflow

```mermaid
flowchart TB
  BEAT[Celery beat] --> PREDICT[Predict all patients]
  PREDICT --> QUEUE[Auto queue interventions]
  QUEUE --> RETRY[Retry failed deliveries]
  PREDICT --> MONITOR[Risk threshold monitor]
  PREDICT --> REFRESH[Analytics refresh]
```

## Database relationships

```mermaid
erDiagram
  USER ||--|| PATIENT : profile
  USER ||--|| DOCTOR : profile
  PATIENT ||--o{ APPOINTMENT : schedules
  PATIENT ||--o{ PATIENT_TREATMENT : receives
  PATIENT ||--o{ PAYMENT : pays
  USER ||--o{ NOTIFICATION : receives
  PATIENT ||--o{ AI_PREDICTION : predicted
  AI_PREDICTION ||--|| SHAP_EXPLANATION : explains
  PATIENT ||--o{ AI_GENERATED_MESSAGE : messaged
  AI_GENERATED_MESSAGE ||--o{ DELIVERY_TRACKING : delivered
  PATIENT ||--o{ INTERVENTION_LOG : logged
```
