from apps.treatments.models import Treatment


def get_treatments_queryset(user):
    return Treatment.objects.filter(is_active=True)
