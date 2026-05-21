import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.ai_interventions.models import (
    AIGeneratedMessage,
    DeliveryStatus,
    DeliveryTracking,
    InterventionLog,
    MessageType,
)
from apps.ai_interventions.services.generator import generate_message
from apps.ai_predictions.models import AIPrediction, ModelType, ModelVersion, RiskLevel, ShapExplanation
from apps.ai_predictions.services.dataset import _ensure_doctors, _ensure_treatments, _get_or_create_user, generate_synthetic_data
from apps.ai_predictions.services.features import FEATURE_NAMES, build_patient_features
from apps.ai_predictions.services.risk import classify_risk
from apps.appointments.models import Appointment, AppointmentStatus, AttendanceStatus
from apps.notifications.models import Notification, NotificationType
from apps.patient_treatments.models import PatientTreatment, TreatmentStatus
from apps.patients.models import Gender, Patient
from apps.payments.models import Payment, PaymentMethod, PaymentStatus
from apps.treatments.models import Treatment
from apps.users.models import UserRole


class Command(BaseCommand):
    help = "Seed curated demo data for live presentations."

    def add_arguments(self, parser):
        parser.add_argument("--patients", type=int, default=250)
        parser.add_argument("--doctors", type=int, default=12)
        parser.add_argument("--seed", type=int, default=42)
        parser.add_argument("--skip-synthetic", action="store_true")
        parser.add_argument("--force-predictions", action="store_true")
        parser.add_argument("--keep-hero-data", action="store_true")

    def handle(self, *args, **options):
        rng = random.Random(options["seed"])
        treatments = _ensure_treatments()
        doctors = _ensure_doctors(rng, options["doctors"])

        run_synthetic = not options["skip_synthetic"]

        if run_synthetic:
            generate_synthetic_data(
                num_patients=options["patients"],
                num_doctors=options["doctors"],
                seed=options["seed"],
            )

        model_version = _ensure_demo_model()
        reset_hero = not options["keep_hero_data"]

        hero_patients = _seed_hero_patients(
            rng=rng,
            doctors=doctors,
            treatments=treatments,
            model_version=model_version,
            reset=reset_hero,
        )

        background = _seed_background_predictions(
            rng=rng,
            model_version=model_version,
            skip_ids={patient.id for patient in hero_patients},
            force=options["force_predictions"],
        )

        self.stdout.write(self.style.SUCCESS("Demo dataset prepared."))
        self.stdout.write(f"- hero_patients: {len(hero_patients)}")
        for key, value in background.items():
            self.stdout.write(f"- {key}: {value}")


def _ensure_demo_model() -> ModelVersion:
    active = ModelVersion.objects.filter(is_active=True).order_by("-trained_at").first()
    if active:
        if not active.metrics:
            active.metrics = {
                "auc": 0.823,
                "precision": 0.78,
                "recall": 0.74,
                "f1": 0.76,
                "brier": 0.18,
            }
            active.calibration = {"notes": "Demo calibration"}
            active.feature_names = active.feature_names or FEATURE_NAMES
            active.save(update_fields=["metrics", "calibration", "feature_names", "updated_at"])
        return active

    return ModelVersion.objects.create(
        name="DentalAI XGBoost Demo",
        model_type=ModelType.XGBOOST,
        is_active=True,
        model_path="models/demo-model.pkl",
        metrics={
            "auc": 0.823,
            "precision": 0.78,
            "recall": 0.74,
            "f1": 0.76,
            "brier": 0.18,
        },
        calibration={"notes": "Demo calibration"},
        feature_names=FEATURE_NAMES,
        hyperparameters={"max_depth": 4, "learning_rate": 0.1, "n_estimators": 220},
        data_summary={"notes": "Demo-ready synthetic dataset"},
    )


def _update_timestamps(model, timestamp):
    model.__class__.objects.filter(pk=model.pk).update(
        created_at=timestamp,
        updated_at=timestamp,
    )


def _reset_patient_data(patient):
    Appointment.objects.filter(patient=patient).delete()
    PatientTreatment.objects.filter(patient=patient).delete()
    Payment.objects.filter(patient=patient).delete()
    Notification.objects.filter(user=patient.user).delete()
    DeliveryTracking.objects.filter(message__patient=patient).delete()
    AIGeneratedMessage.objects.filter(patient=patient).delete()
    InterventionLog.objects.filter(patient=patient).delete()
    ShapExplanation.objects.filter(patient=patient).delete()
    AIPrediction.objects.filter(patient=patient).delete()


def _find_treatment(name: str, treatments: list[Treatment]) -> Treatment:
    for treatment in treatments:
        if treatment.name == name:
            return treatment
    return treatments[0]


def _seed_hero_patients(*, rng, doctors, treatments, model_version, reset: bool):
    now = timezone.now()
    hero_definitions = [
        {
            "email": "maya.iyer@demo.dentalai",
            "first_name": "Maya",
            "last_name": "Iyer",
            "gender": Gender.FEMALE,
            "language": "hi",
            "story": "High risk dropout",
            "treatment": {"name": "Root Canal", "status": TreatmentStatus.ON_HOLD, "progress": 25, "start_days": 150},
            "appointments": [
                {"days": 140, "status": AppointmentStatus.COMPLETED, "attendance": AttendanceStatus.PRESENT, "reason": "Consult"},
                {"days": 110, "status": AppointmentStatus.COMPLETED, "attendance": AttendanceStatus.PRESENT, "reason": "Follow-up"},
                {"days": 45, "status": AppointmentStatus.NO_SHOW, "attendance": AttendanceStatus.ABSENT, "reason": "Treatment"},
                {"days": 18, "status": AppointmentStatus.NO_SHOW, "attendance": AttendanceStatus.ABSENT, "reason": "Treatment"},
                {"days": 7, "status": AppointmentStatus.CANCELLED, "attendance": AttendanceStatus.PENDING, "reason": "Review"},
            ],
            "payments": [
                {"days": 60, "amount": 3200, "status": PaymentStatus.FAILED, "method": PaymentMethod.CARD},
                {"days": 30, "amount": 2800, "status": PaymentStatus.PENDING, "method": PaymentMethod.UPI},
            ],
            "notifications": [
                {"days": 15, "title": "Payment reminder", "type": NotificationType.PAYMENT, "read": False},
                {"days": 12, "title": "Missed visit follow-up", "type": NotificationType.REMINDER, "read": True},
            ],
            "interventions": [
                {"days": 10, "message_type": MessageType.MISSED_FOLLOWUP, "language": "hi", "status": DeliveryStatus.FAILED},
                {"days": 4, "message_type": MessageType.MOTIVATIONAL, "language": "hi", "status": DeliveryStatus.DELIVERED},
            ],
            "predictions": [
                {"days": 40, "prob": 0.62},
                {"days": 18, "prob": 0.74},
                {"days": 3, "prob": 0.86},
            ],
        },
        {
            "email": "rohan.patel@demo.dentalai",
            "first_name": "Rohan",
            "last_name": "Patel",
            "gender": Gender.MALE,
            "language": "en",
            "story": "Improving adherence",
            "treatment": {"name": "Clear Aligners", "status": TreatmentStatus.IN_PROGRESS, "progress": 78, "start_days": 180},
            "appointments": [
                {"days": 60, "status": AppointmentStatus.NO_SHOW, "attendance": AttendanceStatus.ABSENT, "reason": "Alignment"},
                {"days": 30, "status": AppointmentStatus.COMPLETED, "attendance": AttendanceStatus.PRESENT, "reason": "Alignment"},
                {"days": 14, "status": AppointmentStatus.COMPLETED, "attendance": AttendanceStatus.PRESENT, "reason": "Check-in"},
                {"days": 3, "status": AppointmentStatus.COMPLETED, "attendance": AttendanceStatus.PRESENT, "reason": "Progress"},
                {"days": -10, "status": AppointmentStatus.SCHEDULED, "attendance": AttendanceStatus.PENDING, "reason": "Review"},
            ],
            "payments": [
                {"days": 45, "amount": 4200, "status": PaymentStatus.PAID, "method": PaymentMethod.CARD},
                {"days": 10, "amount": 3000, "status": PaymentStatus.PAID, "method": PaymentMethod.UPI},
            ],
            "notifications": [
                {"days": 9, "title": "Appointment reminder", "type": NotificationType.APPOINTMENT, "read": True},
            ],
            "interventions": [
                {"days": 9, "message_type": MessageType.APPOINTMENT_REMINDER, "language": "en", "status": DeliveryStatus.DELIVERED},
            ],
            "predictions": [
                {"days": 40, "prob": 0.72},
                {"days": 20, "prob": 0.55},
                {"days": 2, "prob": 0.36},
            ],
        },
        {
            "email": "neha.singh@demo.dentalai",
            "first_name": "Neha",
            "last_name": "Singh",
            "gender": Gender.FEMALE,
            "language": "ta",
            "story": "Payment risk",
            "treatment": {"name": "Implant Prep", "status": TreatmentStatus.IN_PROGRESS, "progress": 55, "start_days": 120},
            "appointments": [
                {"days": 50, "status": AppointmentStatus.COMPLETED, "attendance": AttendanceStatus.PRESENT, "reason": "Consult"},
                {"days": 25, "status": AppointmentStatus.COMPLETED, "attendance": AttendanceStatus.PRESENT, "reason": "Implant"},
                {"days": 5, "status": AppointmentStatus.COMPLETED, "attendance": AttendanceStatus.PRESENT, "reason": "Review"},
            ],
            "payments": [
                {"days": 40, "amount": 5200, "status": PaymentStatus.PENDING, "method": PaymentMethod.CARD},
                {"days": 20, "amount": 2600, "status": PaymentStatus.FAILED, "method": PaymentMethod.CARD},
                {"days": 5, "amount": 2000, "status": PaymentStatus.PENDING, "method": PaymentMethod.UPI},
            ],
            "notifications": [
                {"days": 8, "title": "Payment reminder", "type": NotificationType.PAYMENT, "read": False},
                {"days": 5, "title": "Care team update", "type": NotificationType.GENERAL, "read": True},
            ],
            "interventions": [
                {"days": 6, "message_type": MessageType.MOTIVATIONAL, "language": "ta", "status": DeliveryStatus.DELIVERED},
            ],
            "predictions": [
                {"days": 30, "prob": 0.44},
                {"days": 5, "prob": 0.55},
            ],
        },
        {
            "email": "arjun.mehta@demo.dentalai",
            "first_name": "Arjun",
            "last_name": "Mehta",
            "gender": Gender.MALE,
            "language": "te",
            "story": "Missed appointment",
            "treatment": {"name": "Scaling + Polishing", "status": TreatmentStatus.ACTIVE, "progress": 40, "start_days": 60},
            "appointments": [
                {"days": 30, "status": AppointmentStatus.COMPLETED, "attendance": AttendanceStatus.PRESENT, "reason": "Cleaning"},
                {"days": 12, "status": AppointmentStatus.RESCHEDULED, "attendance": AttendanceStatus.PENDING, "reason": "Cleaning"},
                {"days": 7, "status": AppointmentStatus.COMPLETED, "attendance": AttendanceStatus.PRESENT, "reason": "Rescheduled"},
                {"days": 2, "status": AppointmentStatus.NO_SHOW, "attendance": AttendanceStatus.ABSENT, "reason": "Review"},
                {"days": -4, "status": AppointmentStatus.SCHEDULED, "attendance": AttendanceStatus.PENDING, "reason": "Follow-up"},
            ],
            "payments": [
                {"days": 20, "amount": 1400, "status": PaymentStatus.PAID, "method": PaymentMethod.CASH},
            ],
            "notifications": [
                {"days": 3, "title": "Appointment reminder", "type": NotificationType.APPOINTMENT, "read": True},
            ],
            "interventions": [
                {"days": 3, "message_type": MessageType.APPOINTMENT_REMINDER, "language": "te", "status": DeliveryStatus.DELIVERED},
            ],
            "predictions": [
                {"days": 20, "prob": 0.5},
                {"days": 2, "prob": 0.68},
            ],
        },
        {
            "email": "sara.khan@demo.dentalai",
            "first_name": "Sara",
            "last_name": "Khan",
            "gender": Gender.FEMALE,
            "language": "en",
            "story": "Successful intervention",
            "treatment": {"name": "Braces Plan", "status": TreatmentStatus.IN_PROGRESS, "progress": 88, "start_days": 200},
            "appointments": [
                {"days": 60, "status": AppointmentStatus.NO_SHOW, "attendance": AttendanceStatus.ABSENT, "reason": "Adjustment"},
                {"days": 45, "status": AppointmentStatus.COMPLETED, "attendance": AttendanceStatus.PRESENT, "reason": "Adjustment"},
                {"days": 20, "status": AppointmentStatus.COMPLETED, "attendance": AttendanceStatus.PRESENT, "reason": "Adjustment"},
                {"days": 5, "status": AppointmentStatus.COMPLETED, "attendance": AttendanceStatus.PRESENT, "reason": "Review"},
            ],
            "payments": [
                {"days": 30, "amount": 3500, "status": PaymentStatus.PAID, "method": PaymentMethod.CARD},
                {"days": 7, "amount": 2200, "status": PaymentStatus.PAID, "method": PaymentMethod.UPI},
            ],
            "notifications": [
                {"days": 14, "title": "Treatment encouragement", "type": NotificationType.TREATMENT, "read": True},
            ],
            "interventions": [
                {"days": 14, "message_type": MessageType.TREATMENT_ENCOURAGEMENT, "language": "en", "status": DeliveryStatus.DELIVERED},
                {"days": 5, "message_type": MessageType.APPOINTMENT_REMINDER, "language": "en", "status": DeliveryStatus.DELIVERED},
            ],
            "predictions": [
                {"days": 50, "prob": 0.81},
                {"days": 20, "prob": 0.62},
                {"days": 2, "prob": 0.44},
            ],
        },
        {
            "email": "kabir.joshi@demo.dentalai",
            "first_name": "Kabir",
            "last_name": "Joshi",
            "gender": Gender.MALE,
            "language": "en",
            "story": "Steady low risk",
            "treatment": {"name": "Composite Filling", "status": TreatmentStatus.COMPLETED, "progress": 100, "start_days": 60},
            "appointments": [
                {"days": 40, "status": AppointmentStatus.COMPLETED, "attendance": AttendanceStatus.PRESENT, "reason": "Filling"},
                {"days": 20, "status": AppointmentStatus.COMPLETED, "attendance": AttendanceStatus.PRESENT, "reason": "Follow-up"},
                {"days": 3, "status": AppointmentStatus.COMPLETED, "attendance": AttendanceStatus.PRESENT, "reason": "Review"},
                {"days": -14, "status": AppointmentStatus.SCHEDULED, "attendance": AttendanceStatus.PENDING, "reason": "Check-in"},
            ],
            "payments": [
                {"days": 25, "amount": 1800, "status": PaymentStatus.PAID, "method": PaymentMethod.CASH},
            ],
            "notifications": [
                {"days": 12, "title": "Care tips", "type": NotificationType.GENERAL, "read": True},
            ],
            "interventions": [
                {"days": 12, "message_type": MessageType.EDUCATIONAL, "language": "en", "status": DeliveryStatus.DELIVERED},
            ],
            "predictions": [
                {"days": 25, "prob": 0.22},
                {"days": 2, "prob": 0.18},
            ],
        },
    ]

    heroes = []

    for idx, hero in enumerate(hero_definitions):
        user, created = _get_or_create_user(
            hero["email"],
            {
                "role": UserRole.PATIENT,
                "first_name": hero["first_name"],
                "last_name": hero["last_name"],
                "phone": f"9{rng.randint(100000000, 999999999)}",
                "preferred_language": hero["language"],
            },
        )
        if not created and user.role != UserRole.PATIENT:
            continue
        user.role = UserRole.PATIENT
        user.preferred_language = hero["language"]
        user.first_name = hero["first_name"]
        user.last_name = hero["last_name"]
        user.save(update_fields=["role", "preferred_language", "first_name", "last_name", "updated_at"])

        patient, _ = Patient.objects.get_or_create(
            user=user,
            defaults={
                "date_of_birth": (now.date() - timedelta(days=rng.randint(20 * 365, 55 * 365))),
                "gender": hero["gender"],
                "address": f"{rng.randint(20, 98)} Aurora Street",
            },
        )

        if reset:
            _reset_patient_data(patient)

        doctor = doctors[idx % len(doctors)]
        treatment = _find_treatment(hero["treatment"]["name"], treatments)
        treatment_status = hero["treatment"]["status"]
        started_at = now.date() - timedelta(days=hero["treatment"]["start_days"])
        completed_at = None
        if treatment_status == TreatmentStatus.COMPLETED:
            completed_at = now.date() - timedelta(days=20)

        PatientTreatment.objects.create(
            patient=patient,
            treatment=treatment,
            doctor=doctor,
            status=treatment_status,
            progress_percent=hero["treatment"]["progress"],
            started_at=started_at,
            completed_at=completed_at,
            notes=hero["story"],
        )

        rescheduled_source = None
        for appt in hero["appointments"]:
            scheduled_at = now - timedelta(days=abs(appt["days"]))
            if appt["days"] < 0:
                scheduled_at = now + timedelta(days=abs(appt["days"]))
            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                scheduled_at=scheduled_at,
                duration_minutes=rng.choice([30, 40, 50]),
                status=appt["status"],
                attendance=appt["attendance"],
                reason=appt["reason"],
                rescheduled_from=rescheduled_source,
            )
            if appt["status"] == AppointmentStatus.RESCHEDULED:
                rescheduled_source = appointment
            else:
                rescheduled_source = None

        for pay in hero["payments"]:
            payment_date = now.date() - timedelta(days=pay["days"])
            Payment.objects.create(
                patient=patient,
                amount=pay["amount"],
                status=pay["status"],
                payment_date=payment_date,
                method=pay["method"],
                description="Treatment installment",
            )

        for notif in hero["notifications"]:
            created_at = now - timedelta(days=notif["days"])
            notification = Notification.objects.create(
                user=patient.user,
                title=notif["title"],
                body="Automated reminder from DentalAI",
                notification_type=notif["type"],
                is_read=notif["read"],
                read_at=created_at if notif["read"] else None,
                metadata={"hero": True},
            )
            _update_timestamps(notification, created_at)

        for msg in hero["interventions"]:
            message = generate_message(
                patient=patient,
                actor=None,
                message_type=msg["message_type"],
                language=msg["language"],
                preview=False,
                channel="in_app",
            )
            created_at = now - timedelta(days=msg["days"])
            AIGeneratedMessage.objects.filter(pk=message.pk).update(
                delivery_status=msg["status"],
                created_at=created_at,
                updated_at=created_at,
            )
            DeliveryTracking.objects.create(
                message=message,
                channel="in_app",
                status=msg["status"],
                attempt=1,
                last_attempt_at=created_at,
                delivered_at=created_at if msg["status"] == DeliveryStatus.DELIVERED else None,
                language=message.language,
                metadata={"demo": True},
                error_message="Delivery failed" if msg["status"] == DeliveryStatus.FAILED else "",
            )
            Notification.objects.filter(metadata__ai_message_id=str(message.id)).update(
                is_read=(msg["status"] == DeliveryStatus.DELIVERED),
                read_at=created_at if msg["status"] == DeliveryStatus.DELIVERED else None,
            )

        features = build_patient_features(patient)
        predictions = []
        for prediction in hero["predictions"]:
            prob = float(prediction["prob"])
            risk_level = classify_risk(prob)
            created_at = now - timedelta(days=prediction["days"])
            prediction_obj = AIPrediction.objects.create(
                patient=patient,
                model_version=model_version,
                probability=prob,
                risk_level=risk_level,
                features=features,
                prediction_source="demo",
            )
            _update_timestamps(prediction_obj, created_at)
            predictions.append(prediction_obj)

        if predictions:
            _create_shap_explanation(predictions[-1], features)

        heroes.append(patient)

    return heroes


def _create_shap_explanation(prediction: AIPrediction, features: dict):
    base_value = 0.35
    shap_values = {name: 0.0 for name in FEATURE_NAMES}
    shap_values["visit_miss_rate"] = round(features.get("visit_miss_rate", 0) * 0.6, 3)
    shap_values["consecutive_misses"] = round(min(features.get("consecutive_misses", 0) / 4, 1) * 0.35, 3)
    shap_values["overdue_payment_days"] = round(min(features.get("overdue_payment_days", 0) / 60, 1) * 0.3, 3)
    shap_values["notification_response_rate"] = round(-features.get("notification_response_rate", 0) * 0.25, 3)
    shap_values["treatment_completion_pct"] = round(-(features.get("treatment_completion_pct", 0) / 100) * 0.2, 3)

    top_features = sorted(
        [
            {
                "feature": name,
                "value": features.get(name, 0),
                "impact": value,
            }
            for name, value in shap_values.items()
        ],
        key=lambda item: abs(item["impact"]),
        reverse=True,
    )[:6]

    ShapExplanation.objects.update_or_create(
        prediction=prediction,
        defaults={
            "patient": prediction.patient,
            "model_version": prediction.model_version,
            "base_value": base_value,
            "shap_values": shap_values,
            "top_features": top_features,
            "feature_values": features,
        },
    )


def _seed_background_predictions(*, rng, model_version, skip_ids, force: bool):
    now = timezone.now()
    patients = Patient.objects.exclude(id__in=skip_ids)
    created = 0
    skipped = 0

    for patient in patients:
        if not force and AIPrediction.objects.filter(patient=patient).exists():
            skipped += 1
            continue
        features = build_patient_features(patient)
        base = 0.18
        base += features.get("visit_miss_rate", 0) * 0.55
        base += min(features.get("overdue_payment_days", 0) / 90, 1) * 0.2
        base += (1 - features.get("notification_response_rate", 0)) * 0.15
        base += (1 - min(features.get("treatment_completion_pct", 0) / 100, 1)) * 0.1
        base = max(0.05, min(base, 0.9))

        prev_prob = max(0.05, min(base + rng.uniform(-0.08, 0.08), 0.95))
        latest_prob = max(0.05, min(base + rng.uniform(-0.05, 0.05), 0.95))

        prev_days = rng.randint(14, 30)
        latest_days = rng.randint(0, 12)

        prev_pred = AIPrediction.objects.create(
            patient=patient,
            model_version=model_version,
            probability=prev_prob,
            risk_level=classify_risk(prev_prob),
            features=features,
            prediction_source="demo",
        )
        _update_timestamps(prev_pred, now - timedelta(days=prev_days))

        latest_pred = AIPrediction.objects.create(
            patient=patient,
            model_version=model_version,
            probability=latest_prob,
            risk_level=classify_risk(latest_prob),
            features=features,
            prediction_source="demo",
        )
        _update_timestamps(latest_pred, now - timedelta(days=latest_days))

        created += 2

    return {
        "predictions_created": created,
        "predictions_skipped": skipped,
        "model_version": model_version.name,
    }
