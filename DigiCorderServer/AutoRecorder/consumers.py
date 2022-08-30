import json
from turtle import update
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from .models import Active_T6, Completed_T6_Sortie, Message




class DashboardConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'test'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    # def disconnect(self, code):
    #     return super().disconnect(code)

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        txmessage = text_data_json['lolmessage']
        newMessage = Message.objects.create(message=txmessage)
        print(text_data_json)

    #     async_to_sync(self.channel_layer.group_send)(
    #         self.room_group_name,
    #         {
    #             'type': 'chat_message',
    #             'message':txmessage
    #         }
    #     )
 
    def lolmessage(self, event):
        txmessage = event['message']
        self.send(text_data=json.dumps({
            'type':'lolmessage',
            'message':txmessage
        }))

    def t6Update(self, event):
        txmessage = event['message']
        self.send(text_data=json.dumps({
            'type':'t6Update',
            'message':txmessage
        }))

