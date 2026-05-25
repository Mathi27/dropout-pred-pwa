import json
from urllib.parse import parse_qs

import jwt
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings


class RealtimeConsumer(AsyncJsonWebsocketConsumer):
    """Simple realtime consumer that authenticates using a JWT token passed
    as a `token` query parameter and subscribes the connection to a set of
    groups based on the user's id and role.

    This consumer expects tokens signed with the Django `SECRET_KEY` (HS256).
    """

    async def connect(self):
        # Parse token from query string
        qs = parse_qs(self.scope.get("query_string", b"").decode())
        token = qs.get("token", [None])[0]

        user = None
        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = payload.get(settings.SIMPLE_JWT.get("USER_ID_CLAIM", "user_id"))
                if user_id:
                    user = await sync_to_async(self._get_user)(user_id)
            except Exception:
                user = None

        # Attach user to scope for convenience
        self.scope["user"] = user

        await self.accept()

        # Subscribe to groups
        if user:
            await self.channel_layer.group_add(self._user_group(user.id), self.channel_name)
            role = getattr(user, "role", None)
            if role:
                await self.channel_layer.group_add(self._role_group(role), self.channel_name)

            # patient/doctor specific groups
            try:
                from apps.patients.models import Patient
                from apps.doctors.models import Doctor

                patient = await sync_to_async(lambda u: Patient.objects.filter(user=u).first())(user)
                if patient:
                    await self.channel_layer.group_add(self._patient_group(patient.id), self.channel_name)

                doctor = await sync_to_async(lambda u: Doctor.objects.filter(user=u).first())(user)
                if doctor:
                    await self.channel_layer.group_add(self._doctor_group(doctor.id), self.channel_name)
            except Exception:
                # If related models are missing, ignore subscription
                pass

    async def disconnect(self, code):
        user = self.scope.get("user")
        if user:
            await self.channel_layer.group_discard(self._user_group(user.id), self.channel_name)
            role = getattr(user, "role", None)
            if role:
                await self.channel_layer.group_discard(self._role_group(role), self.channel_name)

    async def send_event(self, event):
        # Received from channel layer: forward payload to client
        payload = event.get("payload")
        if payload is None:
            return
        await self.send_json(payload)

    @staticmethod
    def _user_group(user_id: int) -> str:
        return f"user_{user_id}"

    @staticmethod
    def _role_group(role: str) -> str:
        return f"role_{role}"

    @staticmethod
    def _patient_group(patient_id: int) -> str:
        return f"patient_{patient_id}"

    @staticmethod
    def _doctor_group(doctor_id: int) -> str:
        return f"doctor_{doctor_id}"

    @staticmethod
    def _get_user(user_id: int):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
