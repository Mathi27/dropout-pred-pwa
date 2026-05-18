from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.analytics import get_admin_analytics_cached, get_doctor_analytics
from apps.core.permissions import IsAdmin, IsDoctorOrAdmin
from apps.core.querysets import get_doctor_profile


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok", "service": "dentalai-api"})


class AdminAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        return Response(get_admin_analytics_cached())


class DoctorAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]

    def get(self, request):
        doctor = get_doctor_profile(request.user)
        if not doctor:
            return Response({"detail": "Doctor profile not found."}, status=404)
        return Response(get_doctor_analytics(doctor))
