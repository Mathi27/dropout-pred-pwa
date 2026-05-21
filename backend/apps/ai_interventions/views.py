from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai_interventions.models import AIGeneratedMessage
from apps.ai_interventions.serializers import AIGeneratedMessageSerializer, InterventionLogSerializer
from apps.ai_interventions.services.automation import queue_interventions_for_high_risk
from apps.ai_interventions.services.delivery import retry_delivery, simulate_delivery
from apps.ai_interventions.services.generator import generate_message
from apps.ai_interventions.services.history import get_intervention_logs, get_patient_messages
from apps.ai_interventions.services.metrics import get_intervention_metrics
from apps.core.permissions import IsAdmin, IsDoctorOrAdmin
from apps.core.querysets import filter_patients_for_user, get_patient_profile
from apps.patients.models import Patient
from apps.users.models import UserRole


def _resolve_patient(request, patient_id: str | None):
    if request.user.role == UserRole.PATIENT:
        profile = get_patient_profile(request.user)
        if not profile:
            return None
        if patient_id and str(profile.id) != str(patient_id):
            return None
        return profile
    if not patient_id:
        return None
    qs = filter_patients_for_user(Patient.objects.select_related("user"), request.user)
    return qs.filter(pk=patient_id).first()


class MessagePreviewView(APIView):
    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]

    def post(self, request):
        patient_id = request.data.get("patient_id")
        if not patient_id:
            return Response({"detail": "patient_id is required."}, status=400)
        patient = _resolve_patient(request, patient_id)
        if not patient:
            return Response({"detail": "Patient not found."}, status=404)
        message_type = request.data.get("message_type")
        language = request.data.get("language")
        message = generate_message(
            patient=patient,
            actor=request.user,
            message_type=message_type,
            language=language,
            preview=True,
        )
        return Response(AIGeneratedMessageSerializer(message).data, status=201)


class MessageGenerateView(APIView):
    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]

    def post(self, request):
        patient_id = request.data.get("patient_id")
        if not patient_id:
            return Response({"detail": "patient_id is required."}, status=400)
        patient = _resolve_patient(request, patient_id)
        if not patient:
            return Response({"detail": "Patient not found."}, status=404)
        message_type = request.data.get("message_type")
        language = request.data.get("language")
        channel = request.data.get("channel", "in_app")
        message = generate_message(
            patient=patient,
            actor=request.user,
            message_type=message_type,
            language=language,
            preview=False,
            channel=channel,
        )
        return Response(AIGeneratedMessageSerializer(message).data, status=201)


class PatientCommunicationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        patient_id = request.query_params.get("patient_id")
        if not patient_id and request.user.role != UserRole.PATIENT:
            return Response({"detail": "patient_id is required."}, status=400)
        patient = _resolve_patient(request, patient_id)
        if not patient:
            return Response({"detail": "Patient not found or not accessible."}, status=404)
        limit = int(request.query_params.get("limit", "30"))
        messages = get_patient_messages(patient, limit=limit)
        return Response(AIGeneratedMessageSerializer(messages, many=True).data)


class InterventionHistoryView(APIView):
    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]

    def get(self, request):
        patient_id = request.query_params.get("patient_id")
        if not patient_id:
            if request.user.role == UserRole.ADMIN:
                logs = get_intervention_logs()
                return Response(InterventionLogSerializer(logs, many=True).data)
            return Response({"detail": "patient_id is required."}, status=400)
        patient = _resolve_patient(request, patient_id)
        if not patient:
            return Response({"detail": "Patient not found or not accessible."}, status=404)
        logs = get_intervention_logs(patient=patient)
        return Response(InterventionLogSerializer(logs, many=True).data)


class InterventionMetricsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        return Response(get_intervention_metrics())


class DeliverySimulateView(APIView):
    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]

    def post(self, request):
        message_id = request.data.get("message_id")
        if not message_id:
            return Response({"detail": "message_id is required."}, status=400)
        try:
            message = AIGeneratedMessage.objects.get(pk=message_id)
        except AIGeneratedMessage.DoesNotExist:
            return Response({"detail": "Message not found."}, status=404)
        if not _resolve_patient(request, str(message.patient_id)):
            return Response({"detail": "Message not found."}, status=404)
        tracking = simulate_delivery(message=message, actor=request.user)
        return Response({"delivery": tracking.status, "message_id": str(message.id)})


class DeliveryRetryView(APIView):
    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]

    def post(self, request):
        message_id = request.data.get("message_id")
        if not message_id:
            return Response({"detail": "message_id is required."}, status=400)
        try:
            message = AIGeneratedMessage.objects.get(pk=message_id)
        except AIGeneratedMessage.DoesNotExist:
            return Response({"detail": "Message not found."}, status=404)
        if not _resolve_patient(request, str(message.patient_id)):
            return Response({"detail": "Message not found."}, status=404)
        tracking = retry_delivery(message=message, actor=request.user)
        return Response({"delivery": tracking.status, "message_id": str(message.id)})


class InterventionQueueView(APIView):
    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]

    def post(self, request):
        def _parse_int(value, default=None):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        min_days = _parse_int(request.data.get("min_days"))
        max_per_run = _parse_int(request.data.get("max_per_run"))
        result = queue_interventions_for_high_risk(
            actor=request.user,
            source="manual",
            min_days_between=min_days,
            max_per_run=max_per_run,
        )
        return Response(result)
