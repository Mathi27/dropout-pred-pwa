import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from apps.users.managers import UserManager


class UserRole(models.TextChoices):
    PATIENT = "patient", "Patient"
    DOCTOR = "doctor", "Doctor"
    RECEPTIONIST = "receptionist", "Receptionist"
    ADMIN = "admin", "Admin"


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=20, blank=True, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.PATIENT,
        db_index=True,
    )
    clinic_id = models.UUIDField(null=True, blank=True, db_index=True)
    preferred_language = models.CharField(max_length=10, default="en")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def save(self, *args, **kwargs):
        if self.role == UserRole.ADMIN:
            self.is_staff = True
        super().save(*args, **kwargs)


class OTPVerification(models.Model):
    """OTP-ready structure for patient phone/email auth (Phase 2+)."""

    class OTPPurpose(models.TextChoices):
        LOGIN = "login", "Login"
        REGISTER = "register", "Register"
        RESET = "reset", "Password Reset"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="otp_verifications",
        null=True,
        blank=True,
    )
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    code_hash = models.CharField(max_length=128)
    purpose = models.CharField(max_length=20, choices=OTPPurpose.choices)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "otp_verifications"
        indexes = [
            models.Index(fields=["email", "purpose"]),
            models.Index(fields=["phone", "purpose"]),
        ]

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at
