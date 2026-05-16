import django_filters
from django.db.models import Q

from apps.patients.models import Patient


class PatientFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    gender = django_filters.CharFilter(field_name="gender")
    ordering = django_filters.OrderingFilter(
        fields=(("created_at", "created_at"), ("user__last_name", "name")),
    )

    class Meta:
        model = Patient
        fields = ["gender"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(user__first_name__icontains=value)
            | Q(user__last_name__icontains=value)
            | Q(user__email__icontains=value)
        )
