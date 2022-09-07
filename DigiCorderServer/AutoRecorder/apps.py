import os
import threading
import asyncio
import time
from django.apps import AppConfig
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async

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
        t1 = threading.Thread(target=task1, args=(threading.current_thread().name,), name='t1')
        t1.start()
            
def task1(parentThreadName):
    import http.client
    import json
    from AutoRecorder.models import ActiveAircraft

    conn = http.client.HTTPSConnection("adsbexchange-com1.p.rapidapi.com")

    headers = {
        'X-RapidAPI-Key': "e7a36b9597msh0954cc7e057677dp160f6fjsn5e333eceedc4",
        'X-RapidAPI-Host': "adsbexchange-com1.p.rapidapi.com"
        }
    
    while True:
        conn.request("GET", "/v2/lat/36.3393/lon/-97.9131/dist/10/", headers=headers)
        res = conn.getresponse()
        data = res.read()
        jsondata = json.loads(data)
        for aircraft in jsondata['ac']:
            try:

                if str(aircraft["t"]) == "TEX2" and str(aircraft["alt_baro"]) != "ground":
                    logger.debug(aircraft['r'] + " is about to be updated or created...")
                    T6, created = ActiveAircraft.objects.get_or_create(
                        tailNumber=aircraft["r"][-3:] #,
                    )

                    T6.callSign=aircraft["flight"]
                    #takeoffTime=aircraft[""],              need takeoff logic
                    #solo=aircraft["solo"],                 need solo callsign db
                    #formation=aircraft[""],                need form callsign db
                    #crossCountry=aircraft[""],             need logic/callsign db
                    T6.localFlight=True                       #default until ^ is implemented
                    #inEastsidePattern=aircraft[""],        need pattern geometry logic
                    T6.emergency=False if aircraft["emergency"] == "none" else True
                    T6.groundSpeed=aircraft['gs']
                    T6.latitude=aircraft['lat']
                    T6.longitude=aircraft['lon']
                    T6.track=aircraft['track']
                    T6.squawk=aircraft['squawk']
                    T6.seen=aircraft['seen']
                    T6.rssi=aircraft['rssi']
                    T6.state="Airborne"
                    T6.save()
                    #signals.displayActiveT6s(ActiveAircraft, T6, created)
                    logger.debug("Success!")   

                # either initial takeoff, touch and go, or final landing
                # if aircraft["t"] is "TEX2" and aircraft["alt_baro"] is "ground":
                #     T6, created = ActiveAircraft.objects.get_or_create(
                #         tailNumber=aircraft["r"][-3:],
                #         callSign=aircraft["flight"],
                #         takeoffTime=aircraft["takeoffTime"],
                #         Comments=aircraft["Comments"],
                #         #solo=aircraft["solo"],                 need solo callsign db
                #         #formation=aircraft[""],                need form callsign db
                #         #crossCountry=aircraft[""],             need logic/callsign db
                #         localFlight=True,                       #default until ^ is implemented
                #         #inEastsidePattern=aircraft[""],        need pattern geometry logic
                #         emergency=False if aircraft["emergency"] is "none" else True,
                #     )
            except KeyError as e:
                logger.debug('KeyError in aircraft ' + str(e) + "; however, this is ok.")

        killSignal = True
        threads_list = threading.enumerate()
        
        for thread in threads_list:
            if thread.name is parentThreadName and thread.is_alive() is True:
                killSignal = False
        
        if killSignal is False:
            time.sleep(1)
            continue
        else:
            os.environ['ENABLE_ADSB'] = 'True'
            return