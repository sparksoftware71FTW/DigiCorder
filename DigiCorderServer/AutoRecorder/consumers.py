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
from .models import ActiveAircraft, ActiveAircraftManager, CompletedSortie, Message, NextTakeoffData, Runway, RunwayManager
import traceback
import logging
logger = logging.getLogger(__name__)

# This is the implementation of the DashboardConsumer class, which is a Channels 
# consumer for the dashboard of the application. The consumer handles the 
# WebSocket connection between the server and the client.
#
# The consumer listens for incoming WebSocket messages from the client, and based 
# on the message type, it performs the necessary actions such as saving the message 
# data to the database or sending updates to the client. The consumer also sends 
# initial updates to the client when the WebSocket connection is established, 
# including the list of active aircraft and the Next Takeoff Data.
#
# The consumer makes use of Channels' asynchronous programming capabilities and 
# uses Django's database_sync_to_async decorator to ensure that database queries 
# are executed in a synchronous manner. The consumer also uses Django's serialization 
# framework to serialize querysets to JSON so that they can be easily sent over 
# the WebSocket connection.
#
# The consumer has methods for handling different types of messages, such as 
# nextTOMessage and rwyUpdate. These methods send updates to the client using 
# the send method, which sends a text message over the WebSocket connection.
#
# The consumer also has methods for saving data to the database, such as saveMessage 
# and saveNextTOMessage, which use Django's ORM to create new objects in the database.
#
# Overall, the DashboardConsumer is an important part of the application, 
# responsible for handling the WebSocket connection and sending updates 
# between the server and the client.

# See https://channels.readthedocs.io/en/stable/ for more information on Channels.

class DashboardConsumer(AsyncWebsocketConsumer):
    """
    This class is a Channels consumer for the dashboard of the application. It handles the WebSocket connection
    between the server and the client. The consumer listens for incoming WebSocket messages from the client and 
    performs necessary actions such as saving data regarding the next takeoff on a particular runway to the database or sending updates to the client. 
    It makes use of Channels' asynchronous programming capabilities and Django's database_sync_to_async decorator 
    and serialization framework to ensure seamless communication over the WebSocket connection.
    """


    async def connect(self):
        try:
            """
            This function is called when the WebSocket is handshaking, 
            i.e. when the WebSocket is being established between the client and the server.
            
            It sends initial updates to the client, including the list of active aircrafts 
            and the Next Takeoff Data. It also sets up the WebSocket connection 
            so that the consumer can listen for incoming messages from the client.
            """

            self.user = self.scope["user"]
            if self.user.is_staff is True:
                pass
            else:
                logger.warn(
                    "Non-staff user tried to access the data feed... " + str(self.user))
                self.close()
                return

            # TODO Check user's per-runway permissions, and add/create message groups per runway based on those permissions.
            # 'test' group gets all runway permissions
            self.room_group_name = 'test'
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

            channel_layer = layers.get_channel_layer()
            nextTOMessages = await database_sync_to_async(get_next_takeoff_update_messages)()

            # runways = await database_sync_to_async(RunwayManager.getAllRunways)()

            async for runway in Runway.objects.all():
                rwyMessage, rwyMetaData = await database_sync_to_async(ActiveAircraftManager.get_Acft_queryset_update_message)(runway)
                await channel_layer.group_send(
                    'test',
                    {
                        'type': 'rwyUpdate',
                        'runway': runway.name,
                        'message': rwyMessage,
                        'meta': rwyMetaData
                    }
                )

            for msg in nextTOMessages:
                await channel_layer.group_send(
                    'test',
                    {
                        'type': 'nextTOMessage',
                        'runway': msg['runway'],
                        'data': msg
                    }
                )
            # logger.debug("Sending initial ActiveAircraft list. Message value is: " + str(t38message))
        except:
            logger.error("Error in Connect Asynchronous Function")
            logger.error(traceback.format_exc())


    def disconnect(self, code):
        try:
            return super().disconnect(code)
        except:
            logger.error("Error in Disconnect Function")
            logger.error(traceback.format_exc())


    async def receive(self, text_data):
        try:
            """
            This function is called when a message is received from the WebSocket. 
            The function processes the message based on its type (currently only messages pertaining to the next takeoff for a particular runway)
            and performs the necessary actions, such as sending updates to all relevant clients and saving data to the database.

            Args:
                text_data (str): The incoming message in the form of a json formatted string.

            Returns:
                None
            """

            text_data_json = json.loads(text_data)
            msgType = text_data_json['type']
            data = text_data_json['data']
            # await database_sync_to_async(self.saveMessage)(txmessage)
            logger.info(text_data_json)
            logger.debug(data)

            if msgType == 'nextTOMessage':
                flags, created = await NextTakeoffData.objects.aget_or_create(runway=await Runway.objects.aget(name=text_data_json['runway']))

                flags.solo = data['solo']
                flags.formationX2 = data['formationX2']
                flags.formationX4 = data['formationX4']

                await database_sync_to_async(self.saveNextTOMessage)(flags)
                logger.info("we did the thing...")
        except:
            logger.error("Error in Receive Asynchronous Function")
            logger.error(traceback.format_exc())


    async def nextTOMessage(self, event):
        try:
            """
            Handle the incoming nextTOMessage event.
            Extract the runway and data information from the event and send it back to the client.

            Parameters:
            event (dict): The incoming event data from the client. It contains the runway and data information.

            Returns:
            None
            """
            runway = event['runway']
            data = event['data']
            logger.debug(str(data))
            await self.send(text_data=json.dumps({
                'type': 'nextTOMessage',
                'runway': runway,
                'data': data
            }))
        except:
            logger.error("Error in nextTOMessage Asynchronous Function")
            logger.error(traceback.format_exc())


    async def rwyUpdate(self, event):
        try:
            """
            Handle a rwyUpdate event - normally triggered by the messageThread functionality in signals.py.
            Used in the consumer to send info to the client upon initial connection.
            Extracts the message, meta, and runway information from the event and sends it to relevant clients.

            Parameters:
            event (dict): The incoming event data from the client. It contains the message, meta, and runway information.

            Returns:
            None
            """
            txmessage = event['message']
            txmetadata = event['meta']
            runway = event['runway']
            logger.debug(str(txmessage))
            await self.send(text_data=json.dumps({
                'type': 'rwyUpdate',
                'runway': runway,
                'message': txmessage,
                'meta': txmetadata
            }))
        except:
            logger.error("Error in rwyUpdate Asynchronous Function")
            logger.error(traceback.format_exc())


    def saveMessage(self, txmessage):
        try:
            """
            Save the incoming message to the database.

            Parameters:
            txmessage (str): The incoming message to be saved.

            Returns:
            None
            """
            newMessage = Message.objects.create(message=txmessage)
        except:
            logger.error("Error in Save Message Function")
            logger.error(traceback.format_exc())


    def saveNextTOMessage(self, nextTOFlags):
        try:
            """
            Save the incoming nextTOFlags to the database.

            Parameters:
            nextTOFlags (NextTakeoffData object): The incoming nextTOFlags to be saved.

            Returns:
            None
            """
            nextTOFlags.save()
        except:
            logger.error("Error in Save Next Takeoff Message Function")
            logger.error(traceback.format_exc())

def toggle(target):
    try:
        """
        Toggle the target value.

        Parameters:
        target (bool): The target value to be toggled.

        Returns:
        bool: The toggled value.
        """
        if target:
            return False
        else:
            return True
    except:
        logger.error("Error in Toggle Function")
        logger.error(traceback.format_exc())


def get_next_takeoff_update_messages():
    try:
        """
        Retrieve all next takeoff data from the database and convert it to a list of dictionaries.

        Returns:
        list: A list of dictionaries containing the next takeoff data.
        """
        nextTOquery = NextTakeoffData.objects.all()
        nextTOMessages = []
        for entry in json.loads(serializers.serialize('json', nextTOquery)):
            nextTOMessages.append(
                entry['fields']
            )
        return nextTOMessages
    except:
        logger.error("Error in Get Next Takeoff Update Messages Function")
        logger.error(traceback.format_exc())

