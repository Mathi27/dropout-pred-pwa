from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.appointments.filters import AppointmentFilter
from apps.appointments.serializers import AppointmentSerializer
from apps.appointments.services import (
    get_appointments_queryset,
    mark_attendance,
    reschedule_appointment,
)
from apps.core.permissions import IsAuthenticated as _  # noqa: F401
from apps.core.permissions import IsReceptionistOrAdmin, IsStaffRole
from rest_framework.permissions import IsAuthenticated
from apps.core.services import create_audit_log
from apps.core.viewsets import SoftDeleteModelViewSet


class AppointmentViewSet(SoftDeleteModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsStaffRole]
    filterset_class = AppointmentFilter
    ordering = ["scheduled_at"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy", "reschedule", "mark_attendance"):
            return [IsAuthenticated(), IsReceptionistOrAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return get_appointments_queryset(self.request.user)

    def perform_create(self, serializer):
        appt = serializer.save()
        create_audit_log(
            actor=self.request.user,
            action="appointment.created",
            resource_type="appointment",
            resource_id=str(appt.id),
        )

    @action(detail=True, methods=["post"], url_path="mark-attendance")
    def mark_attendance_action(self, request, pk=None):
        attendance = request.data.get("attendance")
        if not attendance:
            return Response({"detail": "attendance required"}, status=status.HTTP_400_BAD_REQUEST)
        appt = mark_attendance(
            appointment=self.get_object(),
            attendance=attendance,
            user=request.user,
        )
        return Response(AppointmentSerializer(appt).data)

    @action(detail=True, methods=["post"])
    def reschedule(self, request, pk=None):
        scheduled_at = request.data.get("scheduled_at")
        if not scheduled_at:
            return Response({"detail": "scheduled_at required"}, status=status.HTTP_400_BAD_REQUEST)
        from django.utils.dateparse import parse_datetime

        dt = parse_datetime(scheduled_at)
        if not dt:
            return Response({"detail": "Invalid datetime"}, status=status.HTTP_400_BAD_REQUEST)
        new_appt = reschedule_appointment(
            appointment=self.get_object(),
            new_datetime=dt,
            user=request.user,
        )
        return Response(AppointmentSerializer(new_appt).data, status=status.HTTP_201_CREATED)
