# API Documentation

Base URL: /api/v1
Auth: Bearer JWT in Authorization header.

## Auth
- POST /auth/register/
- POST /auth/login/
- POST /auth/refresh/
- GET /auth/me/
- POST /auth/logout/
- POST /auth/forgot-password/
- POST /auth/otp/request/
- POST /auth/otp/verify/

## Core Resources
All list endpoints support search, ordering, and filters.

- Patients: /patients/
- Doctors: /doctors/
- Receptionists: /receptionists/
- Treatments: /treatments/
- Patient treatments: /patient-treatments/
  - POST /patient-treatments/{id}/update-progress/
- Appointments: /appointments/
  - POST /appointments/{id}/mark-attendance/
  - POST /appointments/{id}/reschedule/
- Notifications: /notifications/
  - GET /notifications/unread-count/
  - POST /notifications/{id}/mark-read/
  - POST /notifications/mark-all-read/
- Clinical notes: /clinical-notes/
- Payments: /payments/
- Audit logs: /audit-logs/
- Users (admin): /users/

## Analytics
- GET /analytics/admin/
- GET /analytics/doctor/

## AI Predictions
- POST /ai/predictions/
- GET /ai/predictions/risk/
- GET /ai/predictions/shap/
- GET /ai/predictions/high-risk/
- GET /ai/predictions/history/
- GET /ai/predictions/timeline/
- GET /ai/predictions/journey/
- GET /ai/models/metrics/
- GET /ai/analytics/risk-trends/
- GET /ai/analytics/overview/

## AI Interventions
- POST /ai/interventions/preview/
- POST /ai/interventions/generate/
- GET /ai/interventions/patient/
- GET /ai/interventions/history/
- GET /ai/interventions/metrics/
- POST /ai/interventions/queue/
- POST /ai/interventions/delivery/simulate/
- POST /ai/interventions/delivery/retry/

## AI Workflows
- POST /ai/workflows/predict-all/
- GET /ai/workflows/status/

## Health
- GET /health/
- GET /health/live/
- GET /health/ready/

## RBAC Summary
Roles: patient, doctor, receptionist, admin.
- patient: own profile, appointments, notifications
- doctor: patient lists, clinical notes, AI insights
- receptionist: scheduling and attendance
- admin: analytics and user management
