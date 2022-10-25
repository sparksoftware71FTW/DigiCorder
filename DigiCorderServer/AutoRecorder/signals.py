import json
from channels import layers
from django.utils import timezone
from django.utils.timezone import timedelta
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.db.models import Q
from django.dispatch import receiver
from django.utils import timezone
from django.core import serializers

from .models import ActiveAircraft, CompletedSortie, Message, Trigger

import logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=ActiveAircraft, dispatch_uid="log_completed_flight")
def log_completed_flight(sender, instance, created, **kwargs):
    if instance.state == "completed sortie":
        #ActiveAircraft.objects.get(pk=instance.tailNumber)
        justLandedAcft = CompletedSortie(
        aircraftType = instance.aircraftType,
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
        justLandedAcft.save()
        instance.delete()
        logger.info("Active -> Completed Transition Occured")


@receiver(post_save, sender=Trigger, dispatch_uid="displayActiveAircraft")
def displayActiveAircraft(sender, instance, created, **kwargs):

    channel_layer = layers.get_channel_layer()
    t6message, t6metadata = get_T6_queryset_update_message()
    async_to_sync(channel_layer.group_send)(
    'test',
        {
            'type':'t6Update',
            'message':t6message,
            'meta': t6metadata
        }
    )
    
    t38message, t38metadata = get_T38_queryset_update_message()
    async_to_sync(channel_layer.group_send)(
    'test',
        {
            'type':'t38Update',
            'message':t38message,
            'meta': t38metadata

        }
    )
    #logger.info("Active Aircraft Signal Triggered")


# @receiver(post_save, sender=ActiveAircraft, dispatch_uid="displayActiveAircraft")
# def displayActiveAircraft(sender, instance, created, **kwargs):

    # channel_layer = layers.get_channel_layer()

    # if instance.aircraftType == "TEX2" or instance.substate == "eastside":
    #     t6message, t6metadata = get_T6_queryset_update_message(sender)
    #     async_to_sync(channel_layer.group_send)(
    #     'test',
    #         {
    #             'type':'t6Update',
    #             'message':t6message,
    #             'meta': t6metadata
    #         }
    #     )
    
    # if instance.aircraftType == "T38" or instance.substate == "shoehorn":
    #     t38message, t38metadata = get_T38_queryset_update_message(sender)
    #     async_to_sync(channel_layer.group_send)(
    #     'test',
    #         {
    #             'type':'t38Update',
    #             'message':t38message,
    #             'meta': t38metadata

    #         }
    #     )
    #logger.info("Active Aircraft Signal Triggered")



def get_ActiveAircraft_queryset():
    """
    Return all active aircraft
    """
    #Question.objects.filter(pub_date__lte=timezone.now())
    return ActiveAircraft.objects.all().order_by('tailNumber')


def get_Message_queryset():
    """
    Return all messages
    """
    #Question.objects.filter(pub_date__lte=timezone.now())
    return Message.objects


def get_T6_queryset_update_message():

    """
    Return all active T-6s serialized with associated metadata
    """
    activeT6query = ActiveAircraft.objects.all().filter(Q(aircraftType='TEX2') | Q(substate='eastside')).order_by('tailNumber')

    activeT6Metadata = {}
    activeT6Metadata['In_Pattern'] = activeT6query.filter(state="in pattern").count()
    activeT6Metadata['Taxiing'] = activeT6query.filter(state="taxiing").count()
    activeT6Metadata['Off_Station'] = activeT6query.filter(state="off station").count()
    activeT6Metadata['Lost_Signal'] = activeT6query.filter(state="lost signal").count()
    activeT6Metadata['dual145'] = []
    for T6 in activeT6query.filter(
        takeoffTime__lt=timezone.now() - timedelta(hours=1, minutes=45)).exclude(
            solo=True).exclude(state='in pattern').exclude(state='taxiing'):
        activeT6Metadata['dual145'].append(T6.callSign)

    activeT6Metadata['solo120'] = []
    for T6 in activeT6query.filter(
        takeoffTime__lt=timezone.now() - timedelta(hours=1, minutes=20)).filter(
            solo=True).exclude(state='in pattern').exclude(state='taxiing'):
            activeT6Metadata['solo120'].append(T6.callSign)

    activeT6Metadata['solosOffStation'] = []
    for T6 in activeT6query.filter(solo=True).exclude(state='in pattern'):
        activeT6Metadata['solosOffStation'].append(T6.callSign)

    activeT6Metadata['solosInPattern'] = []
    for T6 in activeT6query.filter(solo=True).filter(state='in pattern'):
        activeT6Metadata['solosInPattern'].append(T6.callSign)

    activeT6s = serializers.serialize('json', activeT6query)

    logger.debug(json.dumps(activeT6Metadata))
    return activeT6s, json.dumps(activeT6Metadata)


def get_T38_queryset_update_message():
    """
    Return all active T-38s serialized with associated metadata
    """
    activeT38query = ActiveAircraft.objects.all().filter(Q(aircraftType='T38') | Q(substate='shoehorn')).order_by('tailNumber')

    activeT38Metadata = {}
    activeT38Metadata['In_Pattern'] = activeT38query.filter(state="in pattern").count()
    activeT38Metadata['Taxiing'] = activeT38query.filter(state="taxiing").count()
    activeT38Metadata['Off_Station'] = activeT38query.filter(state="off station").count()
    activeT38Metadata['Lost_Signal'] = activeT38query.filter(state="lost signal").count()

    activeT38Metadata['dual120'] = []
    for T38 in activeT38query.filter(
        takeoffTime__lt=timezone.now() - timedelta(hours=1, minutes=20)).exclude(solo=True).exclude(state='taxiing'):
        activeT38Metadata['dual120'].append(T38.callSign)

    activeT38Metadata['solo100'] = []
    for T38 in activeT38query.filter(
        takeoffTime__lt=timezone.now() - timedelta(hours=1, minutes=0)).filter(solo=True).exclude(state='taxiing'):
        activeT38Metadata['solo100'].append(T38.callSign)

    activeT38Metadata['solosOffStation'] = []
    for T38 in activeT38query.filter(solo=True).exclude(state='in pattern'):
        activeT38Metadata['solosOffStation'].append(T38.callSign)

    activeT38Metadata['solosInPattern'] = []
    for T38 in activeT38query.filter(solo=True).filter(state='in pattern'):
        activeT38Metadata['solosInPattern'].append(T38.callSign)

    activeT38s = serializers.serialize('json', activeT38query)

    logger.debug(json.dumps(activeT38Metadata))
    return activeT38s, json.dumps(activeT38Metadata)