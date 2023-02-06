import json
from channels import layers
from django.utils import timezone
from django.utils.timezone import timedelta
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.db.models import Q
from django.dispatch import receiver
from django.core import serializers
from django.contrib.auth.models import Group, User


from .models import ActiveAircraft, ActiveAircraftManager, CompletedSortie, Message, Trigger, NextTakeoffData, Runway, RunwayManager, Airfield, UserDisplayExtra

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
        formationX2=instance.formationX2,
        formationX4=instance.formationX4,
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
        lastState = instance.lastState,
        timestamp = instance.timestamp,
        formTimestamp = instance.formTimestamp
        )
        justLandedAcft.save()
        instance.delete()
        logger.info("Active -> Completed Transition Occured")


@receiver(post_save, sender=NextTakeoffData, dispatch_uid="nextTODisplayUpdate")
def nextTODisplayUpdate(sender, instance, created, **kwargs):

    nextTOMessages = get_next_takeoff_update_messages()
    
    print("Trigger success")

    for msg in nextTOMessages:
        if msg['runway'] == instance.runway.name:
            channel_layer = layers.get_channel_layer()
            async_to_sync(channel_layer.group_send)(
            'test',
                {
                    'type':'nextTOMessage',
                    'runway':msg['runway'],
                    'data':msg        }
            )

@receiver(post_save, sender=Trigger, dispatch_uid="displayActiveAircraft")
def displayActiveAircraft(sender, instance, created, **kwargs):

    channel_layer = layers.get_channel_layer()

    for runway in Runway.objects.all():
        rwyMessage, rwyMetaData = ActiveAircraftManager.get_Acft_queryset_update_message(runway)
        rwy = 't6Update' if runway.name == 'KEND 17L/35R' else 't38Update'   #TODO make this the runway name, and rework the frontend to accept that........
        async_to_sync(channel_layer.group_send)(
        'test',
            {
                'type': rwy,
                'message': rwyMessage,
                'meta': rwyMetaData
            }
        )
        async_to_sync(channel_layer.group_send)(
        'test',
            {
                'type': 'rwyUpdate',
                'runway': runway.name,
                'message': rwyMessage,
                'meta': rwyMetaData
            }
        )




    # t6message, t6metadata = get_T6_queryset_update_message()
    # async_to_sync(channel_layer.group_send)(
    # 'test',
    #     {
    #         'type':'t6Update',
    #         'message':t6message,
    #         'meta': t6metadata
    #     }
    # )
    
    # t38message, t38metadata = get_T38_queryset_update_message()
    # async_to_sync(channel_layer.group_send)(
    # 'test',
    #     {
    #         'type':'t38Update',
    #         'message':t38message,
    #         'meta': t38metadata

    #     }
    # )

################

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



@receiver(post_save, sender=User, dispatch_uid="createUserExtras")
def createUserDisplayExtras(sender, instance, created, **kwargs):

    userGroups = instance.groups.all()
    airfields = []
    for group in userGroups:
        if hasattr(group, 'airfield'):
            airfields.append(group.airfield)
    for airfield in airfields:
        for runway in Runway.objects.filter(airfield=airfield):
            userDisplayExtra, fresh = UserDisplayExtra.objects.get_or_create(runway=runway, user=instance)
            if fresh:
                userDisplayExtra.save()


@receiver(post_save, sender=Airfield, dispatch_uid="createUserGroupForEachAirfield")
def createUserGroupForEachAirfield(sender, instance, created, **kwargs):
    airfieldGroup, created = Group.objects.get_or_create(name=instance.FAAcode)
    if created:
        logger.info("Created user group for airfield: " + airfieldGroup.name)
        instance.userGroup = airfieldGroup
        instance.save()


@receiver(post_save, sender=Runway, dispatch_uid="addRunwayDependencies")
def createRunwayDependencies(sender, instance, created, **kwargs): 

    if created:
        nextTOdata = NextTakeoffData.objects.create(runway=instance,)
        nextTOdata.save()

        airfieldUserGroup = Group.objects.get(name=instance.airfield.FAAcode)
        for user in airfieldUserGroup.user_set.all():
            userDisplayExtras = UserDisplayExtra.objects.create(user=user, runway=instance)
            userDisplayExtras.save()

    






#@receiver(post_save, sender=Runway, dispatch_uid="createUserGroupForEachRunway")
# def createUserGroupForEachRunway(sender, instance, created, **kwargs):
#     runwayGroup, created = Group.objects.get_or_create(name=instance.name)
#     if created:
#         logger.info("Created user group for runway: " + runwayGroup.name)


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

def get_next_takeoff_update_messages():
    nextTOquery = NextTakeoffData.objects.all()
    nextTOMessages = []
    for entry in json.loads(serializers.serialize('json', nextTOquery)):
        nextTOMessages.append(
            entry['fields']
        )
    return nextTOMessages


def get_T6_queryset_update_message():
    """
    Return all active T-6s serialized
    """
    activeT6query = ActiveAircraft.objects.filter(Q(aircraftType='TEX2') | Q(substate='eastside')).order_by('tailNumber')

    activeT6Metadata = {}
    activeT6Metadata['In_Pattern'] = activeT6query.filter(state="in pattern").count() + activeT6query.filter(formationX2=True).filter(state="in pattern").count() + activeT6query.filter(formationX4=True).filter(state="in pattern").count()*3
    activeT6Metadata['Taxiing'] = activeT6query.filter(state="taxiing").count() + activeT6query.filter(formationX2=True).filter(state="taxiing").count() + activeT6query.filter(formationX4=True).filter(state="taxiing").count()*3
    activeT6Metadata['Off_Station'] = activeT6query.filter(state="off station").count() + activeT6query.filter(formationX2=True).filter(state="off station").count() + activeT6query.filter(formationX4=True).filter(state="off station").count()*3
    activeT6Metadata['Lost_Signal'] = activeT6query.filter(state="lost signal").count() + activeT6query.filter(formationX2=True).filter(state="lost signal").count() + activeT6query.filter(formationX4=True).filter(state="lost signal").count()*3

    activeT6Metadata['dual145'] = []
    for T6 in activeT6query.filter(
        takeoffTime__lt=timezone.now() - timedelta(hours=1, minutes=45)).exclude(
            solo=True).exclude(state='taxiing'):
        activeT6Metadata['dual145'].append(T6.callSign)

    activeT6Metadata['solo120'] = []
    for T6 in activeT6query.filter(
        takeoffTime__lt=timezone.now() - timedelta(hours=1, minutes=20)).filter(
            solo=True).exclude(state='taxiing'):
            activeT6Metadata['solo120'].append(T6.callSign)

    activeT6Metadata['solosOffStation'] = []
    for T6 in activeT6query.filter(solo=True).exclude(state='in pattern').exclude(state='taxiing'):
        activeT6Metadata['solosOffStation'].append(T6.callSign)

    activeT6Metadata['solosInPattern'] = []
    for T6 in activeT6query.filter(solo=True).filter(state='in pattern'):
        activeT6Metadata['solosInPattern'].append(T6.callSign)

    activeT6s = serializers.serialize('json', activeT6query)

    #logger.debug(json.dumps(activeT6Metadata))
    return activeT6s, json.dumps(activeT6Metadata)


def get_T38_queryset_update_message():
    """
    Return all active T-6s serialized
    """
    activeT38query = ActiveAircraft.objects.filter(Q(aircraftType='T38') | Q(substate='shoehorn')).order_by('tailNumber')

    activeT38Metadata = {}
    activeT38Metadata['In_Pattern'] = activeT38query.filter(state="in pattern").count() + activeT38query.filter(formationX2=True).filter(state="in pattern").count() + activeT38query.filter(formationX4=True).filter(state="in pattern").count()*3
    activeT38Metadata['Taxiing'] = activeT38query.filter(state="taxiing").count() + activeT38query.filter(formationX2=True).filter(state="taxiing").count() + activeT38query.filter(formationX4=True).filter(state="taxiing").count()*3
    activeT38Metadata['Off_Station'] = activeT38query.filter(state="off station").count() + activeT38query.filter(formationX2=True).filter(state="off station").count() + activeT38query.filter(formationX4=True).filter(state="off station").count()*3
    activeT38Metadata['Lost_Signal'] = activeT38query.filter(state="lost signal").count() + activeT38query.filter(formationX2=True).filter(state="lost signal").count() + activeT38query.filter(formationX4=True).filter(state="lost signal").count()*3

    activeT38Metadata['dual120'] = []
    for T38 in activeT38query.filter(
        takeoffTime__lt=timezone.now() - timedelta(hours=1, minutes=20)).exclude(solo=True).exclude(state='taxiing'):
        activeT38Metadata['dual120'].append(T38.callSign)

    activeT38Metadata['solo100'] = []
    for T38 in activeT38query.filter(
        takeoffTime__lt=timezone.now() - timedelta(hours=1, minutes=0)).filter(solo=True).exclude(state='taxiing'):
        activeT38Metadata['solo100'].append(T38.callSign)

    activeT38Metadata['solosOffStation'] = []
    for T38 in activeT38query.filter(solo=True).exclude(state='in pattern').exclude(state='taxiing'):
        activeT38Metadata['solosOffStation'].append(T38.callSign)

    activeT38Metadata['solosInPattern'] = []
    for T38 in activeT38query.filter(solo=True).filter(state='in pattern'):
        activeT38Metadata['solosInPattern'].append(T38.callSign)

    activeT38s = serializers.serialize('json', activeT38query)

    #logger.debug(json.dumps(activeT38Metadata))
    return activeT38s, json.dumps(activeT38Metadata)
 