import json
from channels import layers
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core import serializers

from .models import ActiveAircraft, CompletedSortie, Message

import logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=ActiveAircraft, dispatch_uid="log_completed_flight")
def log_completed_flight(sender, instance, created, **kwargs):
    if instance.state == "completed sortie":
        #ActiveAircraft.objects.get(pk=instance.tailNumber)
        justLandedT6 = CompletedSortie(
        tailNumber=instance.tailNumber,
        callSign=instance.callSign,
        takeoffTime=instance.takeoffTime,
        three55Code=instance.three55Code,
        Comments=instance.Comments,
        landTime=instance.landTime,
        solo=instance.solo,
        formation=instance.formation,
        emergency=instance.emergency,
        natureOfEmergency=instance.natureOfEmergency,
        groundSpeed=instance.groundSpeed,
        latitude=instance.latitude,
        longitude=instance.longitude,
        alt_baro=instance.alt_baro,
        alt_geom=instance.alt_geom,
        track=instance.track,
        squawk=instance.squawk,
        seen=instance.seen,
        rssi=instance.rssi,
        state=instance.state,
        lastState = instance.lastState
        )
        justLandedT6.save()
        instance.delete()
        logger.warning("!!!!!!!!!!!Active -> Completed Transition Occured!!!!!!!!!!!!")


@receiver(post_save, sender=ActiveAircraft, dispatch_uid="displayActiveAircraft")
def displayActiveAircraft(sender, instance, created, **kwargs):
    activeT38s = serializers.serialize('json', sender.objects.filter(aircraftType='T38').order_by('tailNumber'))
    activeT6s = serializers.serialize('json', sender.objects.filter(aircraftType='TEX2').order_by('tailNumber'))
    channel_layer = layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)(
    'test',
        {
            'type':'t6Update',
            'message':activeT6s
        }
    )
    async_to_sync(channel_layer.group_send)(
    'test',
        {
            'type':'t38Update',
            'message':activeT38s
        }
    )
    logger.warning("!!!!!!!!!!!Active Aircraft Signal Triggered!!!!!!!!!!!!")

def get_ActiveAircraft_queryset():
    """
    Return all active aircraft
    """
    #Question.objects.filter(pub_date__lte=timezone.now())
    return ActiveAircraft.objects.all().order_by(
    '-takeoffTime')

def get_Message_queryset():
    """
    Return all messages
    """
    #Question.objects.filter(pub_date__lte=timezone.now())
    return Message.objects