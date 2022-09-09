import asyncio
import json
from time import sleep
from django.db.models.signals import post_save
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from channels import layers
from channels.db import database_sync_to_async
from django.core import serializers

from .models import ActiveAircraft, CompletedSortie, Message

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

        t6message = await database_sync_to_async(self.get_T6_queryset_update_message)()
        t38message = await database_sync_to_async(self.get_T38_queryset_update_message)()
         
        channel_layer = layers.get_channel_layer()
        await channel_layer.group_send(
        'test',
            {
                'type':'t6Update',
                'message':t6message
            }
        )
        await channel_layer.group_send(
        'test',
            {
                'type':'t38Update',
                'message':t38message
            }
        )
        logger.debug("Sending initial ActiveAircraft list. Message value is: " + str(t38message))
        

    # def disconnect(self, code):
    #     return super().disconnect(code)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        txmessage = text_data_json['lolmessage']
        await database_sync_to_async(self.saveMessage)(txmessage)
        logger.debug(text_data_json)

    #     async_to_sync(self.channel_layer.group_send)(
    #         self.room_group_name,
    #         {
    #             'type': 'chat_message',
    #             'message':txmessage
    #         }
    #     )

    def saveMessage(self, txmessage):
        newMessage = Message.objects.create(message=txmessage)

    def get_T6_queryset_update_message(self):
        """
        Return all active T-6s serialized
        """
        activeT6s = serializers.serialize('json', ActiveAircraft.objects.all().filter(aircraftType='TEX2').order_by(
        '-takeoffTime'))
             
        return activeT6s

    def get_T38_queryset_update_message(self):
        """
        Return all active T-6s serialized
        """
        activeT38s = serializers.serialize('json', ActiveAircraft.objects.all().filter(aircraftType='T38').order_by(
        '-takeoffTime'))
             
        return activeT38s
 
    async def lolmessage(self, event):
        txmessage = event['message']
        await self.send(text_data=json.dumps({
            'type':'lolmessage',
            'message':txmessage
        }))


    async def t6Update(self, event):
        txmessage = event['message']
        await self.send(text_data=json.dumps({
            'type':'t6Update',
            'message':txmessage
        }))

    async def t38Update(self, event):
        txmessage = event['message']
        await self.send(text_data=json.dumps({
            'type':'t38Update',
            'message':txmessage
        }))
        logger.debug('!!!!!!! t38Update' + str(txmessage))

