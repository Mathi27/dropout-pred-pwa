import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from apps.users.models import OTPVerification, User


class OTPService:
    """OTP generation and verification stub for Phase 2+ integration."""

    @staticmethod
    def _hash_code(code: str) -> str:
        return hashlib.sha256(code.encode()).hexdigest()

    @classmethod
    def generate_otp(
        cls,
        *,
        purpose: str,
        user: User | None = None,
        email: str = "",
        phone: str = "",
    ) -> tuple[str, OTPVerification]:
        code = f"{secrets.randbelow(10**6):06d}"
        record = OTPVerification.objects.create(
            user=user,
            email=email or (user.email if user else ""),
            phone=phone or (user.phone if user else ""),
            code_hash=cls._hash_code(code),
            purpose=purpose,
            expires_at=timezone.now()
            + timedelta(minutes=getattr(settings, "OTP_EXPIRY_MINUTES", 10)),
        )
        return code, record

    @classmethod
    def verify_otp(cls, *, code: str, purpose: str, email: str = "", phone: str = "") -> OTPVerification | None:
        code_hash = cls._hash_code(code)
        qs = OTPVerification.objects.filter(
            purpose=purpose,
            code_hash=code_hash,
            is_used=False,
        )
        if email:
            qs = qs.filter(email=email)
        if phone:
            qs = qs.filter(phone=phone)

        record = qs.order_by("-created_at").first()
        if not record or record.is_expired:
            return None
        record.is_used = True
        record.save(update_fields=["is_used"])
        return record
