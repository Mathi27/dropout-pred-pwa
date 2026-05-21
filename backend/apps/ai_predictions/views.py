from datetime import timedelta

from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai_predictions.models import AIPrediction, RiskLevel
from apps.ai_predictions.serializers import AIPredictionSerializer, ModelVersionSerializer, ShapExplanationSerializer
from apps.ai_predictions.services.analytics import get_ai_analytics_overview_cached
from apps.ai_predictions.services.monitoring import get_automation_status
from apps.ai_predictions.services.explainability import get_or_create_explanation
from apps.ai_predictions.services.history import get_prediction_history
from apps.ai_predictions.services.journey import build_patient_journey
from apps.ai_predictions.services.metrics import get_active_model_metrics
from apps.ai_predictions.services.predictor import generate_prediction, get_latest_prediction
from apps.ai_predictions.services.timeline import build_patient_timeline
from apps.ai_predictions.services.workflows import predict_all_patients
from apps.ai_interventions.services.automation import queue_interventions_for_high_risk
from apps.core.permissions import IsAdmin, IsDoctorOrAdmin, IsStaffRole
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


class PredictionGenerateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        patient_id = request.data.get("patient_id")
        if not patient_id and request.user.role != UserRole.PATIENT:
            return Response({"detail": "patient_id is required."}, status=400)
        patient = _resolve_patient(request, patient_id)
        if not patient:
            return Response({"detail": "Patient not found or not accessible."}, status=404)
        try:
            prediction = generate_prediction(patient=patient, user=request.user, source="api")
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response(AIPredictionSerializer(prediction).data, status=201)


class PatientRiskView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        patient_id = request.query_params.get("patient_id")
        if not patient_id and request.user.role != UserRole.PATIENT:
            return Response({"detail": "patient_id is required."}, status=400)
        patient = _resolve_patient(request, patient_id)
        if not patient:
            return Response({"detail": "Patient not found or not accessible."}, status=404)
        prediction = get_latest_prediction(patient)
        auto_generate = request.query_params.get("auto") == "true"
        if not prediction and auto_generate:
            try:
                prediction = generate_prediction(patient=patient, user=request.user, source="api")
            except ValueError as exc:
                return Response({"detail": str(exc)}, status=400)
        if not prediction:
            return Response({"detail": "No predictions found."}, status=404)
        return Response(AIPredictionSerializer(prediction).data)


class ShapExplanationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        patient_id = request.query_params.get("patient_id")
        if not patient_id and request.user.role != UserRole.PATIENT:
            return Response({"detail": "patient_id is required."}, status=400)
        patient = _resolve_patient(request, patient_id)
        if not patient:
            return Response({"detail": "Patient not found or not accessible."}, status=404)
        prediction = get_latest_prediction(patient)
        if not prediction:
            try:
                prediction = generate_prediction(patient=patient, user=request.user, source="api")
            except ValueError as exc:
                return Response({"detail": str(exc)}, status=400)
        try:
            explanation = get_or_create_explanation(prediction)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response(ShapExplanationSerializer(explanation).data)


class PredictionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        patient_id = request.query_params.get("patient_id")
        if not patient_id and request.user.role != UserRole.PATIENT:
            return Response({"detail": "patient_id is required."}, status=400)
        patient = _resolve_patient(request, patient_id)
        if not patient:
            return Response({"detail": "Patient not found or not accessible."}, status=404)
        limit = int(request.query_params.get("limit", "25"))
        history = get_prediction_history(patient=patient, limit=limit)
        serializer = AIPredictionSerializer(history, many=True)
        return Response(serializer.data)


class HighRiskPatientsView(APIView):
    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]

    def get(self, request):
        patients_qs = filter_patients_for_user(Patient.objects.select_related("user"), request.user)
        latest_predictions = (
            AIPrediction.objects.filter(patient__in=patients_qs)
            .order_by("patient_id", "-created_at")
            .distinct("patient_id")
        )
        high_risk = latest_predictions.filter(risk_level=RiskLevel.HIGH)
        return Response(AIPredictionSerializer(high_risk, many=True).data)


class ModelMetricsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        metrics = get_active_model_metrics()
        if not metrics:
            return Response({"detail": "No active model available."}, status=404)
        model_version, payload = metrics
        return Response(
            {
                "model_version": ModelVersionSerializer(model_version).data,
                "metrics": payload.get("metrics", {}),
                "calibration": payload.get("calibration", {}),
            }
        )


class RiskTrendsView(APIView):
    permission_classes = [IsAuthenticated, IsStaffRole]

    def get(self, request):
        days = int(request.query_params.get("days", "30"))
        since = timezone.now().date() - timedelta(days=days)
        patients_qs = filter_patients_for_user(Patient.objects.all(), request.user)
        predictions = AIPrediction.objects.filter(
            patient__in=patients_qs,
            created_at__date__gte=since,
        )
        by_day = (
            predictions.annotate(day=TruncDate("created_at"))
            .values("day", "risk_level")
            .order_by("day")
        )
        counts = {}
        for row in by_day:
            day = row["day"].isoformat()
            risk = row["risk_level"]
            counts.setdefault(day, {"low": 0, "medium": 0, "high": 0})
            counts[day][risk] += 1
        payload = [
            {"date": day, **levels, "total": sum(levels.values())}
            for day, levels in sorted(counts.items())
        ]
        return Response(payload)


class AnalyticsOverviewView(APIView):
    permission_classes = [IsAuthenticated, IsStaffRole]

    def get(self, request):
        days = int(request.query_params.get("days", "30"))
        payload = get_ai_analytics_overview_cached(request.user, days=days)
        return Response(payload)


class PatientRiskTimelineView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        patient_id = request.query_params.get("patient_id")
        if not patient_id and request.user.role != UserRole.PATIENT:
            return Response({"detail": "patient_id is required."}, status=400)
        patient = _resolve_patient(request, patient_id)
        if not patient:
            return Response({"detail": "Patient not found or not accessible."}, status=404)
        days = int(request.query_params.get("days", "120"))
        events = build_patient_timeline(patient, days=days)
        return Response({"events": events})


class PatientJourneyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        patient_id = request.query_params.get("patient_id")
        if not patient_id and request.user.role != UserRole.PATIENT:
            return Response({"detail": "patient_id is required."}, status=400)
        patient = _resolve_patient(request, patient_id)
        if not patient:
            return Response({"detail": "Patient not found or not accessible."}, status=404)
        days = int(request.query_params.get("days", "180"))
        payload = build_patient_journey(patient, days=days)
        return Response(payload)


class PredictAllPatientsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        def _parse_int(value, default=None):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        min_days = _parse_int(request.data.get("min_days"))
        max_patients = _parse_int(request.data.get("max_patients"))
        auto_queue = str(request.data.get("auto_queue", "true")).lower() in ("true", "1", "yes")

        result = predict_all_patients(
            actor=request.user,
            source="manual",
            min_days=min_days,
            max_patients=max_patients,
        )
        payload = {"predictions": result}
        if auto_queue:
            payload["queue"] = queue_interventions_for_high_risk(actor=request.user, source="manual")
        return Response(payload)


class AutomationStatusView(APIView):
    permission_classes = [IsAuthenticated, IsStaffRole]

    def get(self, request):
        days = int(request.query_params.get("days", "7"))
        return Response(get_automation_status(days=days))
