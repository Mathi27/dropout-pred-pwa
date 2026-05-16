import django_filters

from apps.appointments.models import Appointment


class AppointmentFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status")
    attendance = django_filters.CharFilter(field_name="attendance")
    patient = django_filters.UUIDFilter(field_name="patient_id")
    doctor = django_filters.UUIDFilter(field_name="doctor_id")
    scheduled_after = django_filters.DateTimeFilter(field_name="scheduled_at", lookup_expr="gte")
    scheduled_before = django_filters.DateTimeFilter(field_name="scheduled_at", lookup_expr="lte")
    date = django_filters.DateFilter(field_name="scheduled_at", lookup_expr="date")
    ordering = django_filters.OrderingFilter(fields=(("scheduled_at", "scheduled_at"), ("status", "status")))

    class Meta:
        model = Appointment
        fields = ["status", "attendance", "patient", "doctor"]
