from contextlib import nullcontext
import os
from sqlite3 import Timestamp
import threading
import asyncio
import time
from django.apps import AppConfig
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from shapely import geometry
from datetime import datetime


import logging
logger = logging.getLogger(__name__)

class AutoRecorderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'AutoRecorder'

    def ready(self):

        from AutoRecorder import signals
        #This is where the background thread will kick off...
        #Make sure to add a is_running database model and a corresponding check 
        #to make sure you're not adding multiple threads...
        #Also! This thread WILL interact with the database specified in settings.py... NOT a testing db.
        #Make sure we've got only one background thread running...
        enable_adsb = os.environ.get('ENABLE_ADSB') 
        if enable_adsb == 'False':
            return
        os.environ['ENABLE_ADSB'] = 'False'
        logger.debug("ready() thread is: " + threading.current_thread().name)
        t6 = threading.Thread(target=task1, args=(threading.current_thread().name, "TEX2"), name='T6Thread')
        t6.start()
            
def task1(parentThreadName, aircraftType):
    import http.client
    import json
    from AutoRecorder.models import ActiveAircraft

    conn = http.client.HTTPSConnection("adsbexchange-com1.p.rapidapi.com")

    headers = {
        'X-RapidAPI-Key': "e7a36b9597msh0954cc7e057677dp160f6fjsn5e333eceedc4",
        'X-RapidAPI-Host': "adsbexchange-com1.p.rapidapi.com"
        }
    
    while True:
        conn.request("GET", "/v2/lat/36.3393/lon/-97.9131/dist/50/", headers=headers)
        res = conn.getresponse()
        data = res.read()
        jsondata = json.loads(data)
        updatedAircraftList = []
        for aircraft in jsondata['ac']:
            try:

                if str(aircraft["t"]) == aircraftType and str(aircraft["alt_baro"]) != "ground":
                    logger.debug(aircraft['r'] + " is about to be updated or created...")
                    T6, created = ActiveAircraft.objects.get_or_create(
                        tailNumber=aircraft["r"][-3:] #,
                    )

                    T6.callSign=aircraft["flight"]
                    T6.aircraftType=aircraft['t']
                    #solo=aircraft["solo"],                 need solo callsign db
                    #formation=aircraft[""],                need form callsign db
                    T6.emergency=False if aircraft["emergency"] == "none" else True
                    T6.groundSpeed=aircraft['gs']
                    T6.latitude=aircraft['lat']
                    T6.longitude=aircraft['lon']
                    T6.track=aircraft['track']
                    T6.squawk=aircraft['squawk']
                    T6.seen=aircraft['seen']
                    T6.rssi=aircraft['rssi']
                    T6.lastState = T6.state
                    position = geometry.Point(T6.latitude, T6.longitude)
                    if inPattern(position) and T6.groundSpeed > 40 and T6.alt_baro != "ground":
                        T6.state="in pattern"
                        if T6.lastState == "taxiing":
                            T6.takeoffTime = datetime.now()
                    elif inPattern(position) and T6.groundSpeed < 40 and T6.alt_baro == "ground":
                        T6.state="taxiiing"
                        if T6.lastState == "in pattern":
                            T6.landTime = datetime.now()
                    elif inPattern(position) == False:
                        T6.state="off station" 
                    T6.timestamp=datetime.now()
                    T6.save()
                    logger.debug("Success!")   
                    updatedAircraftList.append(T6.tailNumber)         

            except KeyError as e:
                logger.debug('KeyError in aircraft ' + str(e) + "; however, this is ok.")

        aircraftNotUpdated = getAircraftNotUpdated(updatedAircraftList)

        if aircraftNotUpdated is not None:
            for T6 in aircraftNotUpdated:
                if T6.timestamp or T6.landTime or T6.state or T6.lastState is None:
                    continue
                if (T6.timestamp - datetime.now()).total_seconds() > 120: 
                    if T6.landTime == None:
                        T6.lastState = T6.state
                        T6.state = "lost signal"
                    else:
                        T6.lastState = T6.state
                        T6.state = "completed sortie"
                if(T6.timestamp - datetime.now()).total_hours() > 4:
                    T6.lastState = T6.state
                    T6.state = "completed sortie"
                T6.save()

        killSignal = True
        threads_list = threading.enumerate()
        
        for thread in threads_list:
            if thread.name is parentThreadName and thread.is_alive() is True:
                killSignal = False
        
        if killSignal is False:
            time.sleep(10)
            continue
        else:
            os.environ['ENABLE_ADSB'] = 'True'
            return

def inPattern(position):
    patternCoords = [(36.34274909853927, -97.85060096116348), (36.38501763547715, -97.85340389119733), (36.37083992357469, -97.91998997477251), (36.37083992899921, -97.91998998150338), (36.45457130802796, -97.88064193324243), (36.43822747970118, -97.94454597209545), (36.34029761411401, -98.01874780036422), (36.27950096822119, -97.96044005727545), (36.27950096279858, -97.96044005727501), (36.27950095737597, -97.96044005727457)]
    patternGeo = geometry.Polygon(patternCoords)
    if ((position.within(patternGeo))):
        return True
    else:
        return False

def getAircraftNotUpdated(updatedAircraftList):
    from AutoRecorder.models import ActiveAircraft
    return ActiveAircraft.objects.exclude(tailNumber__in=updatedAircraftList)
