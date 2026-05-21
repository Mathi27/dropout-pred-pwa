import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.users.models import UserRole

User = get_user_model()
logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "phone",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "clinic_id",
            "preferred_language",
            "email_verified",
            "phone_verified",
            "is_active",
            "created_at",
        )
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    password_confirm = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    role = serializers.ChoiceField(
        choices=[c for c in UserRole.choices if c[0] != UserRole.ADMIN],
        default=UserRole.PATIENT,
        required=False,
    )
    phone = serializers.CharField(required=False, allow_blank=True, max_length=20)
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    preferred_language = serializers.CharField(required=False, default="en", max_length=10)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "phone",
            "role",
            "preferred_language",
        )

    def validate_email(self, value: str) -> str:
        return value.strip().lower()

    def validate_role(self, value: str) -> str:
        if value == UserRole.ADMIN:
            raise serializers.ValidationError("Cannot self-register as admin.")
        if value not in UserRole.values:
            raise serializers.ValidationError("Invalid role.")
        return value

    def validate_password(self, value: str) -> str:
        attrs = getattr(self, "initial_data", {}) or {}
        candidate = User(
            email=str(attrs.get("email", "")).strip().lower(),
            first_name=str(attrs.get("first_name", "")),
            last_name=str(attrs.get("last_name", "")),
        )
        try:
            validate_password(value, user=candidate)
        except DjangoValidationError as exc:
            logger.debug("Register password validation failed: %s", exc.messages)
            raise serializers.ValidationError(list(exc.messages)) from exc
        return value

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.pop("password_confirm", None)
        if password != password_confirm:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        attrs.setdefault("role", UserRole.PATIENT)
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["email"] = user.email
        if user.clinic_id:
            token["clinic_id"] = str(user.clinic_id)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data
