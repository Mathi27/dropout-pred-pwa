# Architecture Overview

DentalAI is a modular AI healthcare platform with separate layers for API, analytics, AI workflows, and UI.

## Core components
- Frontend: React + Vite + Tailwind
- Backend: Django 5 + DRF + JWT + Celery
- Data: PostgreSQL
- Queue: Redis
- ML: scikit-learn + XGBoost + SHAP

## Service boundaries
- apps/ai_predictions: model training, inference, analytics
- apps/ai_interventions: message generation and delivery simulation
- apps/core: analytics aggregations, health checks
- apps/appointments, patients, payments, notifications: domain data

## Architecture notes
- Role-based access is enforced in DRF permissions
- AI predictions use stored model artifacts and feature schema
- Automation uses Celery beat schedules and workflow services

## Diagrams
See docs/diagrams.md for system and workflow diagrams.
