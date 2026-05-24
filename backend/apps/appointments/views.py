from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.appointments.filters import AppointmentFilter
from apps.appointments.models import AppointmentStatus
from apps.appointments.serializers import AppointmentSerializer
from apps.appointments.services import (
    get_appointments_queryset,
    mark_attendance,
    reschedule_appointment,
)
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsReceptionistOrAdmin
from apps.core.querysets import get_patient_profile
from apps.core.services import create_audit_log
from apps.core.viewsets import SoftDeleteModelViewSet
from apps.users.models import UserRole
from apps.notifications.services import create_notification
from apps.notifications.models import NotificationType


class AppointmentViewSet(SoftDeleteModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = AppointmentFilter
    ordering = ["scheduled_at"]

    def get_permissions(self):
        if self.action in ("create", "partial_update", "reschedule"):
            if getattr(self.request.user, "role", None) == UserRole.PATIENT:
                return [IsAuthenticated()]
            return [IsAuthenticated(), IsReceptionistOrAdmin()]
        if self.action in ("mark_attendance", "update", "destroy"):
            return [IsAuthenticated(), IsReceptionistOrAdmin()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        if getattr(request.user, "role", None) == UserRole.PATIENT:
            profile = get_patient_profile(request.user)
            if not profile:
                return Response({"detail": "Patient profile not found."}, status=status.HTTP_400_BAD_REQUEST)
            data = request.data.copy()
            data["patient_id"] = str(profile.id)
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return super().create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if getattr(request.user, "role", None) == UserRole.PATIENT:
            if request.data.get("status") != AppointmentStatus.CANCELLED:
                return Response(
                    {"detail": "Patients may only cancel appointments."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        return super().partial_update(request, *args, **kwargs)

    def get_queryset(self):
        return get_appointments_queryset(self.request.user)

    def perform_create(self, serializer):
        appt = serializer.save()
        create_audit_log(
            actor=self.request.user,
            action="appointment.created",
            resource_type="appointment",
            resource_id=str(appt.id),
            metadata={
                "patient_id": str(appt.patient.id) if getattr(appt, "patient", None) else None,
                "doctor_id": str(appt.doctor.id) if getattr(appt, "doctor", None) else None,
                "scheduled_at": appt.scheduled_at.isoformat() if getattr(appt, "scheduled_at", None) else None,
            },
        )

        # Create an in-app notification for the patient so they see the booking
        try:
            if getattr(appt.patient, "user", None):
                create_notification(
                    user=appt.patient.user,
                    title="Appointment scheduled",
                    body=f"Your appointment is scheduled for {appt.scheduled_at.isoformat()}",
                    notification_type=NotificationType.APPOINTMENT,
                    actor=self.request.user,
                    metadata={"appointment_id": str(appt.id)},
                )
        except Exception:
            # Notification failure should not block appointment creation
            pass

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
