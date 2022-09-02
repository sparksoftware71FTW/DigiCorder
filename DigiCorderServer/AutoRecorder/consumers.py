import asyncio
import json
from time import sleep
from django.db.models.signals import post_save
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from channels import layers
from channels.db import database_sync_to_async

from .models import Active_T6, Completed_T6_Sortie, Message

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

        message = await database_sync_to_async(self.get_T6_queryset_update_message)()

        channel_layer = layers.get_channel_layer()
        await channel_layer.group_send(
        'test',
            {
                'type':'t6Update',
                'message':message
            }
        )
        logger.debug("Sending initial Active_T6 list. Message value is: ", message)
        

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
        Return all active T-6s
        """
        #Question.objects.filter(pub_date__lte=timezone.now())
        activeT6s = Active_T6.objects.all().order_by(
        '-takeoffTime')[:]
        message = ""
        for t6 in activeT6s:
            message = message + str(t6.callSign) + "\n"
        return message
 
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

