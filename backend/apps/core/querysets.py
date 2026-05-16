from django.db.models import Q

from apps.users.models import UserRole


def get_patient_profile(user):
    if not user or not user.is_authenticated:
        return None
    return getattr(user, "patient_profile", None)


def get_doctor_profile(user):
    if not user or not user.is_authenticated:
        return None
    return getattr(user, "doctor_profile", None)


def filter_patients_for_user(queryset, user):
    if user.role == UserRole.ADMIN:
        return queryset
    if user.role == UserRole.PATIENT:
        profile = get_patient_profile(user)
        return queryset.filter(pk=profile.pk) if profile else queryset.none()
    if user.role == UserRole.DOCTOR:
        doctor = get_doctor_profile(user)
        if not doctor:
            return queryset.none()
        return queryset.filter(
            Q(patient_treatments__doctor=doctor) | Q(appointments__doctor=doctor)
        ).distinct()
    return queryset


def filter_by_patient_relation(queryset, user, patient_field="patient"):
    if user.role == UserRole.ADMIN:
        return queryset
    if user.role == UserRole.RECEPTIONIST:
        return queryset
    if user.role == UserRole.PATIENT:
        profile = get_patient_profile(user)
        if not profile:
            return queryset.none()
        return queryset.filter(**{patient_field: profile})
    if user.role == UserRole.DOCTOR:
        doctor = get_doctor_profile(user)
        if not doctor:
            return queryset.none()
        return queryset.filter(
            Q(**{f"{patient_field}__patient_treatments__doctor": doctor})
            | Q(**{f"{patient_field}__appointments__doctor": doctor})
        ).distinct()
    return queryset.none()


def filter_notifications_for_user(queryset, user):
    if user.role == UserRole.ADMIN:
        return queryset
    return queryset.filter(user=user)


def filter_appointments_for_user(queryset, user):
    if user.role in (UserRole.ADMIN, UserRole.RECEPTIONIST):
        return queryset
    if user.role == UserRole.PATIENT:
        profile = get_patient_profile(user)
        return queryset.filter(patient=profile) if profile else queryset.none()
    if user.role == UserRole.DOCTOR:
        doctor = get_doctor_profile(user)
        return queryset.filter(doctor=doctor) if doctor else queryset.none()
    return queryset.none()
