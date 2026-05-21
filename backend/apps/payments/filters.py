import django_filters

from apps.payments.models import Payment


class PaymentFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status")
    patient = django_filters.UUIDFilter(field_name="patient_id")
    ordering = django_filters.OrderingFilter(fields=(("payment_date", "payment_date"), ("amount", "amount")))

    class Meta:
        model = Payment
        fields = ["status", "patient"]
