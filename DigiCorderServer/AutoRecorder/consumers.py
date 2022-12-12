import json
from django.utils import timezone
from django.utils.timezone import timedelta
from django.db.models.signals import post_save
from django.db.models import Q
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from channels import layers
from channels.db import database_sync_to_async
from django.core import serializers

from .models import ActiveAircraft, CompletedSortie, Message, NextTakeoffData, Runway

import logging
logger = logging.getLogger(__name__)

class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'test'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        t6message, t6metadata = await database_sync_to_async(self.get_T6_queryset_update_message)()
        t38message, t38metadata = await database_sync_to_async(self.get_T38_queryset_update_message)()
        nextTOMessages = await database_sync_to_async(self.get_next_takeoff_update_messages)()
         
        channel_layer = layers.get_channel_layer()
        await channel_layer.group_send(
        'test',
            {
                'type':'t6Update',
                'message':t6message,
                'meta': t6metadata
            }
        )
        await channel_layer.group_send(
        'test',
            {
                'type':'t38Update',
                'message':t38message,
                'meta':t38metadata
            }
        )
        
        for msg in nextTOMessages:
            await channel_layer.group_send(
                'test',
                {
                    'type':'nextTOMessage',
                    'runway':msg['runway'],
                    'data':msg
                }
            )
        #logger.debug("Sending initial ActiveAircraft list. Message value is: " + str(t38message))
        

    # def disconnect(self, code):
    #     return super().disconnect(code)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        msgType = text_data_json['type']
        data = text_data_json['data']
        # await database_sync_to_async(self.saveMessage)(txmessage)
        logger.info(text_data_json)
        print(data)

        if msgType == 'nextTOMessage':
            flags, created = await NextTakeoffData.objects.aget_or_create(runway=await Runway.objects.aget(name=text_data_json['runway']))
            
            flags.solo = data['solo']
            flags.formationX2 = data['formationX2']
            flags.formationX4 = data['formationX4']
            # match data:
            #     case '2-ship':
            #         flags.formationX2 = self.toggle(flags.formationX2)
            #         logger.info("2-ship triggered")
            #     case '4-ship':
            #         flags.formationX4 = self.toggle(flags.formationX2)
            #         logger.info("4-ship triggered")
            #     case 'solo':
            #         flags.solo = toggle(flags.solo)
            #         logger.info("solo triggered")
            await database_sync_to_async(self.saveNextTOMessage)(flags)
            logger.info("we did the thing...")

    #     async_to_sync(self.channel_layer.group_send)(
    #         self.room_group_name,
    #         {
    #             'type': 'chat_message',
    #             'message':txmessage
    #         }
    #     )
    
    async def nextTOMessage(self, event):
        runway = event['runway']
        data = event['data']
        #logger.debug("!!!!!!!!!!!!!!!!!!!!!!!!!!" + str(data))
        await self.send(text_data=json.dumps({
            'type':'nextTOMessage',
            'runway': runway,
            'data':data
        })) 

    async def lolmessage(self, event):
        txmessage = event['message']
        
        await self.send(text_data=json.dumps({
            'type':'lolmessage',
            'message':txmessage
        }))


    async def t6Update(self, event):
        txmessage = event['message']
        txmetadata = event['meta']
        #logger.debug("!!!!!!!!!!!!!!!!!!!!!!!!!!" + str(txmessage))
        await self.send(text_data=json.dumps({
            'type':'t6Update',
            'message':txmessage,
            'meta':txmetadata
        }))


    async def t38Update(self, event):
        txmessage = event['message']
        txmetadata = event['meta']
        await self.send(text_data=json.dumps({
            'type':'t38Update',
            'message':txmessage,
            'meta':txmetadata
        }))
        #logger.debug('!!!!!!! t38Update' + str(txmessage))


    def saveMessage(self, txmessage):
        newMessage = Message.objects.create(message=txmessage)

    def saveNextTOMessage(self, nextTOFlags):
        nextTOFlags.save()


    def toggle(self, target):
        if target:
            return False
        else:
            return True

    def get_next_takeoff_update_messages(self):
        nextTOquery = NextTakeoffData.objects.all()
        nextTOMessages = []
        for entry in json.loads(serializers.serialize('json', nextTOquery)):
            nextTOMessages.append(
                entry['fields']
            )
        return nextTOMessages

    def get_T6_queryset_update_message(self):
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
    

    def get_T38_queryset_update_message(self):
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
 

def toggle(target):
        if target:
            return False
        else:
            return True