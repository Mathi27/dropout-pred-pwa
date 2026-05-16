from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsAdmin
from apps.core.viewsets import SoftDeleteModelViewSet
from apps.receptionists.serializers import ReceptionistSerializer
from apps.receptionists.services import get_receptionists_queryset


class ReceptionistViewSet(SoftDeleteModelViewSet):
    serializer_class = ReceptionistSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = Receptionist.objects.select_related("user")

    def get_queryset(self):
        return get_receptionists_queryset(self.request.user)
