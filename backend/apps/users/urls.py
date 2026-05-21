from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.users.admin_views import AdminUserViewSet
from apps.users.views import (
    ForgotPasswordView,
    LoginView,
    LogoutView,
    MeView,
    OTPRequestView,
    OTPVerifyView,
    RefreshTokenView,
    RegisterView,
)

router = DefaultRouter()
router.register(r"users", AdminUserViewSet, basename="admin-users")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/refresh/", RefreshTokenView.as_view(), name="auth-refresh"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/forgot-password/", ForgotPasswordView.as_view(), name="auth-forgot-password"),
    path("auth/otp/request/", OTPRequestView.as_view(), name="auth-otp-request"),
    path("auth/otp/verify/", OTPVerifyView.as_view(), name="auth-otp-verify"),
    path("", include(router.urls)),
]
