from apps.receptionists.models import Receptionist
from apps.users.models import UserRole


def get_receptionists_queryset(user):
    if user.role == UserRole.ADMIN:
        return Receptionist.objects.select_related("user")
    return Receptionist.objects.none()
