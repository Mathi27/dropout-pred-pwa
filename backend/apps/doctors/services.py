from apps.doctors.models import Doctor
from apps.users.models import UserRole


def get_doctors_queryset(user):
    qs = Doctor.objects.select_related("user")
    if user.role == UserRole.ADMIN:
        return qs
    if user.role in (UserRole.RECEPTIONIST, UserRole.DOCTOR, UserRole.PATIENT):
        return qs.filter(is_available=True)
    return qs.none()
