from apps.core.querysets import filter_by_patient_relation
from apps.payments.models import Payment
from apps.users.models import UserRole


def get_payments_queryset(user):
    qs = Payment.objects.select_related("patient__user")
    if user.role == UserRole.ADMIN:
        return qs
    return filter_by_patient_relation(qs, user, patient_field="patient")
