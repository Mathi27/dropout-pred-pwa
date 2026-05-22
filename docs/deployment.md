# Deployment Guide

This guide outlines production-ready deployment for DentalAI.

## Overview

DentalAI is split into:
- Backend: Django 5 + DRF + Celery (Gunicorn)
- Frontend: React + Vite (static build)
- Data: PostgreSQL
- Queue: Redis

## Backend (Django)

### Environment

Create backend/.env using backend/.env.production.example as a template. Set:
- DJANGO_SECRET_KEY
- DATABASE_URL
- CELERY_BROKER_URL
- CELERY_RESULT_BACKEND
- CORS_ALLOWED_ORIGINS

Use the production settings module:

```
export DJANGO_SETTINGS_MODULE=config.settings_production
```

### Run (Gunicorn)

```
cd backend
./../scripts/run_backend_prod.sh
```

Recommended Gunicorn tuning:
- GUNICORN_WORKERS: 3-6
- GUNICORN_TIMEOUT: 60

### Celery

Start the worker and beat scheduler in separate processes:

```
cd backend
./../scripts/run_celery_worker.sh
./../scripts/run_celery_beat.sh
```

## Frontend (Vite)

Set frontend/.env from frontend/.env.production.example, then build:

```
./scripts/build_frontend.sh
```

Serve the frontend with Nginx or a static host. Point API requests to:

```
VITE_API_BASE_URL=https://api.yourdomain.com/api/v1
```

## PostgreSQL

Provision a managed PostgreSQL database (Neon, RDS, Render, etc.) or a Dockerized instance. Ensure:
- SSL enabled in production
- Regular backups
- Connection pooling if traffic grows

## Redis

Provision a managed Redis instance and set CELERY_BROKER_URL and CELERY_RESULT_BACKEND.

## Health checks

Use the built-in endpoints:
- GET /api/v1/health/live/
- GET /api/v1/health/ready/

You can automate checks with:

```
./scripts/check_health.sh
```

## Logging

Set DJANGO_LOG_LEVEL to INFO or WARNING for production.

## Recommended runtime

- Backend: 1-2 vCPU, 1-2 GB RAM (more for heavy analytics)
- Celery: separate worker service
- Redis: small instance
- Postgres: managed with backups
