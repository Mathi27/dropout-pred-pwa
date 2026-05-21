import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlparse

from celery.schedules import crontab

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-dev-only-change-in-production")
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() in ("true", "1", "yes")
ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "apps.core",
    "apps.users",
    "apps.patients",
    "apps.doctors",
    "apps.receptionists",
    "apps.treatments",
    "apps.patient_treatments",
    "apps.appointments",
    "apps.notifications",
    "apps.clinical_notes",
    "apps.payments",
    "apps.audit_logs",
    "apps.ai_predictions",
    "apps.ai_interventions",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://dentalai:dentalai_dev@localhost:5432/dentalai",
)


def _database_from_url(url: str) -> dict:
    parsed = urlparse(url)
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": parsed.path.lstrip("/") or "dentalai",
        "USER": parsed.username or "dentalai",
        "PASSWORD": parsed.password or "",
        "HOST": parsed.hostname or "localhost",
        "PORT": str(parsed.port or 5432),
        "OPTIONS": {"sslmode": "require"} if "neon.tech" in (parsed.hostname or "") else {},
    }


DATABASES = {"default": _database_from_url(DATABASE_URL)}

AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if o.strip()
]
CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
}

_access_minutes = int(os.getenv("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", "15"))
_refresh_days = int(os.getenv("JWT_REFRESH_TOKEN_LIFETIME_DAYS", "7"))

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=_access_minutes),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=_refresh_days),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

CELERY_BEAT_SCHEDULE = {
    "ai-daily-prediction-simulation": {
        "task": "apps.ai_predictions.tasks.daily_prediction_simulation_task",
        "schedule": crontab(hour=2, minute=30),
    },
    "ai-intervention-queue": {
        "task": "apps.ai_interventions.tasks.queue_interventions_task",
        "schedule": crontab(minute=0, hour="*/1"),
    },
    "ai-delivery-retries": {
        "task": "apps.ai_interventions.tasks.retry_failed_deliveries_task",
        "schedule": crontab(minute=20, hour="*/2"),
    },
    "ai-analytics-refresh": {
        "task": "apps.ai_predictions.tasks.refresh_analytics_task",
        "schedule": crontab(minute="*/30"),
    },
    "ai-risk-threshold-monitor": {
        "task": "apps.ai_predictions.tasks.monitor_risk_thresholds_task",
        "schedule": crontab(minute=10, hour="*/6"),
    },
}

OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", "10"))
CLINIC_NAME = os.getenv("CLINIC_NAME", "DentalAI Clinic")

AI_PREDICTION_COOLDOWN_DAYS = int(os.getenv("AI_PREDICTION_COOLDOWN_DAYS", "1"))
AI_INTERVENTION_COOLDOWN_DAYS = int(os.getenv("AI_INTERVENTION_COOLDOWN_DAYS", "7"))
AI_INTERVENTION_MAX_QUEUE = int(os.getenv("AI_INTERVENTION_MAX_QUEUE", "200"))
AI_RISK_ESCALATION_DELTA = float(os.getenv("AI_RISK_ESCALATION_DELTA", "0.12"))
AI_RISK_ESCALATION_MIN_PROB = float(os.getenv("AI_RISK_ESCALATION_MIN_PROB", "0.7"))
AI_RISK_ESCALATION_COOLDOWN_DAYS = int(os.getenv("AI_RISK_ESCALATION_COOLDOWN_DAYS", "7"))
AI_RISK_RISING_DELTA = float(os.getenv("AI_RISK_RISING_DELTA", "0.08"))
AI_HIGH_RISK_SHARE_THRESHOLD = float(os.getenv("AI_HIGH_RISK_SHARE_THRESHOLD", "0.25"))
AI_RISK_MONITOR_DAYS = int(os.getenv("AI_RISK_MONITOR_DAYS", "7"))
AI_RISK_MONITOR_MIN_PREDICTIONS = int(os.getenv("AI_RISK_MONITOR_MIN_PREDICTIONS", "25"))
AI_RETRY_MAX_ATTEMPTS = int(os.getenv("AI_RETRY_MAX_ATTEMPTS", "3"))
ADMIN_ANALYTICS_CACHE_TTL = int(os.getenv("ADMIN_ANALYTICS_CACHE_TTL", "300"))
AI_ANALYTICS_CACHE_TTL = int(os.getenv("AI_ANALYTICS_CACHE_TTL", "300"))
