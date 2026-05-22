# Showcase Guide

This guide helps you present DentalAI in demos and portfolio walkthroughs.

## Suggested demo flow
1. Open Executive Analytics for top-level KPIs
2. Inspect AI Insights for risk trends and confidence
3. Open a patient profile for journey timeline
4. Trigger prediction and intervention generation
5. Show intervention delivery metrics

## Demo tips
- Use a seeded dataset for consistent results
- Mention automation workflows (Celery beat)
- Highlight explainability via SHAP

## Demo data

Seed realistic demo data and hero patients:

```
cd backend
python manage.py seed_demo_data
```

Optional flags:
- --skip-synthetic (skip background synthetic data)
- --force-predictions (regenerate predictions for all patients)
- --keep-hero-data (do not reset hero patient stories)

## Demo credentials
Store demo credentials in your environment variables or a secure vault.
