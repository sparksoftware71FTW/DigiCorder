import json
from channels import layers
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Active_T6, Completed_T6_Sortie, Message

@receiver(post_save, sender=Active_T6, dispatch_uid="noDuplicates")
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

@receiver(post_save, sender=Active_T6, dispatch_uid="noDuplicates")
def displayActiveT6s(sender, instance, created, **kwargs):
    activeT6s = get_T6_queryset()
    message = ""
    for t6 in activeT6s:
        message = message + t6.callSign + "\n"

    channel_layer = layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)(
    'test',
        {
            'type':'t6Update',
            'message':message
        }
    )
    print("Signal received. Message value is: ", message)

@receiver(post_save, sender=Message, dispatch_uid="noDuplicates")
def newMessage(sender, instance, created, **kwargs):
    channel_layer = layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)(
    'test',
        {
            'type':'lolmessage',
            'message':instance.message
        }
    )
    print("Signal received. Message db value is: ", instance.message)
 
# def chat_message(self, event):
#     message = event['message']
#     channel_layer = layers.get_channel_layer()

#     async_to_sync(channel_layer.send)(text_data=json.dumps(
#         message
#     ))

def get_T6_queryset():
    """
    Return all active T-6s
    """
    #Question.objects.filter(pub_date__lte=timezone.now())
    return Active_T6.objects.all().order_by(
    '-takeoffTime')[:]

def get_Message_queryset():
    """
    Return all messages
    """
    #Question.objects.filter(pub_date__lte=timezone.now())
    return Message.objects