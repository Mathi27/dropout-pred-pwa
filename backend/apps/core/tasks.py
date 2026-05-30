from __future__ import annotations

from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@shared_task
def publish_audit_event(audit_id: int) -> None:
    """Load the AuditLog and publish a lightweight event payload to
    relevant channel groups so connected clients can react in realtime.

    This function intentionally keeps payloads small and uses best-effort
    broadcasting (exceptions are swallowed) to avoid impacting user flows.
    """
    try:
        from apps.audit_logs.models import AuditLog

        audit = AuditLog.objects.select_related("actor").get(id=audit_id)
    except Exception:
        return

    payload = {
        "action": audit.action,
        "resource_type": audit.resource_type,
        "resource_id": audit.resource_id,
        "metadata": audit.metadata or {},
        "actor_id": audit.actor.id if audit.actor else None,
        "timestamp": audit.created_at.isoformat(),
    }

    groups = set()

    # Always notify the actor (if any)
    if payload.get("actor_id"):
        groups.add(f"user_{payload['actor_id']}")

    # Map specific resource types to interested groups
    try:
        if audit.resource_type == "appointment":
            from celery import shared_task
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer


            def publish_audit_event_sync(audit_id: int) -> None:
                """Synchronous publisher for audit events. Can be called directly from
                Django processes when Celery is not available or when immediate delivery
                is desired (development).
                """
                try:
                    from apps.audit_logs.models import AuditLog

                    audit = AuditLog.objects.select_related("actor").get(id=audit_id)
                except Exception:
                    return

                payload = {
                    "action": audit.action,
                    "resource_type": audit.resource_type,
                    "resource_id": audit.resource_id,
                    "metadata": audit.metadata or {},
                    "actor_id": audit.actor.id if audit.actor else None,
                    "timestamp": audit.created_at.isoformat(),
                }

                groups = set()

                # Always notify the actor (if any)
                if payload.get("actor_id"):
                    groups.add(f"user_{payload['actor_id']}")

                # Map specific resource types to interested groups
                try:
                    if audit.resource_type == "appointment":
                        from apps.appointments.models import Appointment

                        appt = (
                            Appointment.objects.filter(id=audit.resource_id)
                            .select_related("patient__user", "doctor__user")
                            .first()
                        )
                        if appt:
                            if appt.patient and appt.patient.user:
                                groups.add(f"user_{appt.patient.user.id}")
                                groups.add(f"patient_{appt.patient.id}")
                            if appt.doctor and getattr(appt.doctor, "user", None):
                                groups.add(f"user_{appt.doctor.user.id}")
                                groups.add(f"doctor_{appt.doctor.id}")
                        # notify receptionists and doctors broadly so schedules refresh
                        groups.add("role_receptionist")
                        groups.add("role_doctor")

                    elif audit.resource_type in ("notification",):
                        from apps.notifications.models import Notification

                        notif = Notification.objects.filter(id=audit.resource_id).select_related("user").first()
                        if notif and notif.user:
                            groups.add(f"user_{notif.user.id}")

                    elif audit.resource_type in ("patient_treatment",):
                        from apps.patient_treatments.models import PatientTreatment

                        pt = (
                            PatientTreatment.objects.filter(id=audit.resource_id)
                            .select_related("patient__user", "doctor__user")
                            .first()
                        )
                        if pt and pt.patient and pt.patient.user:
                            groups.add(f"user_{pt.patient.user.id}")
                            groups.add(f"patient_{pt.patient.id}")
                        if pt and getattr(pt, "doctor", None) and getattr(pt.doctor, "user", None):
                            groups.add(f"user_{pt.doctor.user.id}")
                            groups.add(f"doctor_{pt.doctor.id}")
                        groups.add("role_doctor")

                    elif audit.resource_type in ("ai_generated_message", "ai_message", "ai_intervention"):
                        from apps.ai_interventions.models import AIGeneratedMessage

                        msg = (
                            AIGeneratedMessage.objects.filter(id=audit.resource_id).select_related("patient__user").first()
                        )
                        if msg and msg.patient and msg.patient.user:
                            groups.add(f"user_{msg.patient.user.id}")
                            groups.add(f"patient_{msg.patient.id}")

                    elif audit.resource_type in ("ai_prediction", "prediction"):
                        from apps.ai_predictions.models import AIPrediction

                        pred = (
                            AIPrediction.objects.filter(id=audit.resource_id)
                            .select_related("patient__user")
                            .first()
                        )
                        if pred and pred.patient and pred.patient.user:
                            groups.add(f"user_{pred.patient.user.id}")
                            groups.add(f"patient_{pred.patient.id}")
                        # doctors should refresh risk dashboards
                        groups.add("role_doctor")

                except Exception:
                    # If any models are missing or lookups fail, keep going with minimal groups
                    pass

                # Also notify role groups for broader dashboards
                # Admins should see operational metrics updates
                groups.add("role_admin")

                channel_layer = get_channel_layer()
                for group in groups:
                    try:
                        async_to_sync(channel_layer.group_send)(group, {"type": "send_event", "payload": payload})
                    except Exception:
                        # Best-effort broadcasting
                        continue


            @shared_task
            def publish_audit_event(audit_id: int) -> None:
                return publish_audit_event_sync(audit_id)
