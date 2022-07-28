from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Active_T6, Completed_T6_Sortie

@receiver(post_save, sender=Active_T6)
def log_completed_flight(sender, instance, created, **kwargs):
    if isinstance(instance.landTime, timezone.datetime):
        #Active_T6.objects.get(pk=instance.tailNumber)
        justLandedT6 = Completed_T6_Sortie(
        tailNumber=instance.tailNumber,
        callSign=instance.callSign,
        takeoffTime=instance.takeoffTime,
        three55Code=instance.three55Code,
        Comments=instance.Comments,
        landTime=instance.landTime,
        solo=instance.solo,
        formation=instance.formation,
        crossCountry=instance.crossCountry,
        localFlight=instance.localFlight,
        inEastsidePattern=instance.inEastsidePattern,
        emergency=instance.emergency,
        natureOfEmergency=instance.natureOfEmergency,
        )
        justLandedT6.save()
        instance.delete()



