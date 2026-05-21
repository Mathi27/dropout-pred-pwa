from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.users.models import User, UserRole


@receiver(post_save, sender=User)
def create_role_profile(sender, instance: User, created: bool, **kwargs):
    if not created:
        return
    if instance.role == UserRole.PATIENT:
        from apps.patients.models import Patient

        Patient.objects.get_or_create(user=instance)
    elif instance.role == UserRole.DOCTOR:
        from apps.doctors.models import Doctor

        Doctor.objects.get_or_create(user=instance)
    elif instance.role == UserRole.RECEPTIONIST:
        from apps.receptionists.models import Receptionist

        Receptionist.objects.get_or_create(user=instance)
