from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Active_T6, Completed_T6_Sortie

@receiver(post_save, sender=Active_T6)
def log_completed_flight(sender, instance, created, **kwargs):
    if isinstance(instance.landTime, timezone.datetime):
        print("!")