# DentalAI PWA

AI-powered dental treatment adherence platform — INAHS 2026 Research .

**Phase 1** delivers monorepo scaffolding, JWT authentication, RBAC foundation, and a responsive dashboard shell.

## Structure

```
dent-pwa/
├── backend/          # Django 5 + DRF + JWT + Celery stubs
├── frontend/         # React 18 + Vite + Tailwind + shadcn/ui
├── ml/               # ML module stub (Phase 4)
├── docker-compose.yml
└── README.md
```

## Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 16 (or `docker compose up -d`)
- Redis (optional for Celery; included in docker-compose)

## Quick start

### 1. Database & Redis (local)

```bash
cd /mnt/stuffs/PROJECTS/dent-pwa
docker compose up -d
```

### 2. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser   # optional
python manage.py runserver
```

API: `http://localhost:8000/api/v1/`

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

App: `http://localhost:5173`

## Environment variables

### Backend (`backend/.env`)

| Variable | Description |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Django secret key |
| `DJANGO_DEBUG` | `True` for development |
| `DATABASE_URL` | PostgreSQL connection string (Neon or local) |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | Default `15` |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | Default `7` |
| `CORS_ALLOWED_ORIGINS` | Frontend origins |
| `CELERY_BROKER_URL` | Redis URL |

**Neon example:**

```
DATABASE_URL=postgresql://user:pass@ep-xxx.ap-south-1.aws.neon.tech/dentalai?sslmode=require
```

### Frontend (`frontend/.env`)

| Variable | Description |
|----------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` |

## Migrations

```bash
cd backend
source .venv/bin/activate
python manage.py makemigrations
python manage.py migrate
```

## API routes (Phase 1)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/health/` | Public | Health check |
| POST | `/api/v1/auth/register/` | Public | Register user |
| POST | `/api/v1/auth/login/` | Public | Login (JWT) |
| POST | `/api/v1/auth/refresh/` | Public | Refresh access token |
| GET | `/api/v1/auth/me/` | Bearer | Current user |
| POST | `/api/v1/auth/logout/` | Bearer | Blacklist refresh token |

## Roles (RBAC)

| Role | Dashboard focus |
|------|-----------------|
| `patient` | Treatment journey (placeholder) |
| `doctor` | Patient risk overview |
| `receptionist` | Schedule & attendance |
| `admin` | Clinic KPIs |

JWT access tokens include `role` and optional `clinic_id` claims.

## Dev servers

```bash
# Terminal 1 — backend
cd backend && source .venv/bin/activate && python manage.py runserver

# Terminal 2 — frontend
cd frontend && npm run dev
```

## Verify setup

```bash
cd backend && .venv/bin/python manage.py check
cd frontend && npm run build
```

## Phase roadmap

- **Phase 1** (current): Auth, RBAC, dashboard shell
- **Phase 2**: UI/UX design system
- **Phase 3**: Full backend APIs + appointments
- **Phase 4**: ML + GenAI integration
- **Phase 5**: PWA offline + push notifications

## License

Research use — INAHS 2026 Paper #110.
