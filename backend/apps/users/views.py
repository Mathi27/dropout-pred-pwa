import logging

from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.models import OTPVerification
from apps.users.serializers import (
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer,
)
from apps.users.services import OTPService

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if settings.DEBUG:
            safe_keys = [k for k in request.data if k not in ("password", "password_confirm")]
            logger.debug("Register attempt fields: %s", safe_keys)

        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            if settings.DEBUG:
                logger.warning("Register validation failed: %s", serializer.errors)
            raise ValidationError(serializer.errors)

        user = serializer.save()
        if settings.DEBUG:
            logger.debug("Register success for user_id=%s role=%s", user.id, user.role)
        refresh = RefreshToken.for_user(user)
        refresh["role"] = user.role
        refresh["email"] = user.email
        if user.clinic_id:
            refresh["clinic_id"] = str(user.clinic_id)
        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


class RefreshTokenView(TokenRefreshView):
    permission_classes = [AllowAny]


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)


class ForgotPasswordView(APIView):
    """Stub: accepts email and returns success (OTP integration in Phase 3+)."""

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email", "")
        if email:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            user = User.objects.filter(email=email).first()
            if user:
                OTPService.generate_otp(purpose=OTPVerification.OTPPurpose.RESET, user=user)
        return Response(
            {"detail": "If an account exists, a reset code has been sent."},
            status=status.HTTP_200_OK,
        )


class OTPRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email", "")
        phone = request.data.get("phone", "")
        purpose = request.data.get("purpose", OTPVerification.OTPPurpose.LOGIN)
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.filter(email=email).first() if email else None
        code, _record = OTPService.generate_otp(
            purpose=purpose, user=user, email=email, phone=phone
        )
        payload = {"detail": "OTP sent.", "expires_in_minutes": 10}
        if request.data.get("debug"):
            payload["debug_code"] = code
        return Response(payload, status=status.HTTP_200_OK)


class OTPVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get("code", "")
        purpose = request.data.get("purpose", OTPVerification.OTPPurpose.LOGIN)
        email = request.data.get("email", "")
        record = OTPService.verify_otp(code=code, purpose=purpose, email=email)
        if not record:
            return Response({"detail": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "OTP verified.", "verified": True})
