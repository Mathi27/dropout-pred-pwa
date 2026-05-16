from rest_framework.permissions import BasePermission

from apps.users.models import UserRole


class IsRole(BasePermission):
    """Allow access only if the user's role is in `allowed_roles`."""

    allowed_roles: tuple[str, ...] = ()

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in self.allowed_roles


class IsPatient(IsRole):
    allowed_roles = (UserRole.PATIENT,)


class IsDoctor(IsRole):
    allowed_roles = (UserRole.DOCTOR,)


class IsReceptionist(IsRole):
    allowed_roles = (UserRole.RECEPTIONIST,)


class IsAdmin(IsRole):
    allowed_roles = (UserRole.ADMIN,)


class IsStaffRole(IsRole):
    """Doctor, receptionist, or admin."""

    allowed_roles = (UserRole.DOCTOR, UserRole.RECEPTIONIST, UserRole.ADMIN)


class IsDoctorOrAdmin(IsRole):
    allowed_roles = (UserRole.DOCTOR, UserRole.ADMIN)


class IsReceptionistOrAdmin(IsRole):
    allowed_roles = (UserRole.RECEPTIONIST, UserRole.ADMIN)
