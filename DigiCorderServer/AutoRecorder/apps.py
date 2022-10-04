from contextlib import nullcontext
import os
import threading
import asyncio
import time
from django.apps import AppConfig
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from shapely import geometry
from django.utils import timezone
from fastkml import kml


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
        threadName = threading.current_thread().name
        logger.debug("ready() thread is: " + threadName)
        ADSBThread = threading.Thread(target=task1, args=(threadName,), name='ADSBThread')
        ADSBThread.start()
            
def task1(parentThreadName):
    logger.info("Starting ADSB Thread")
    import http.client
    import json
    from AutoRecorder.models import ActiveAircraft

    conn = http.client.HTTPSConnection("adsbexchange-com1.p.rapidapi.com")

    headers = {
        'X-RapidAPI-Key': "e7a36b9597msh0954cc7e057677dp160f6fjsn5e333eceedc4",
        'X-RapidAPI-Host': "adsbexchange-com1.p.rapidapi.com"
        }

    # New pattern logic:
    # If any aircraft is in a pattern, add it to active aircraft for displaying
    # Once non-T1/T6/T38 aircraft depart the pattern, delete from active aircraft

    # Either replace "in pattern" state with seperate states for each pattern,
    # or add additional db field for a specific pattern (e.g. 'shoehorn'/'eastside')

    # Rework t6 and t38 messaging functions to send all types of aircraft in the shoehorn
    # or eastside patterns


    while True:
        logger.info("Requesting ADSB Data...")
        conn.request("GET", "/v2/lat/36.3393/lon/-97.9131/dist/250/", headers=headers)
        res = conn.getresponse()
        data = res.read()
        jsondata = json.loads(data)
        updatedAircraftList = []
        for aircraft in jsondata['ac']:
            try:
                if str(aircraft["t"]) == 'TEX2' or str(aircraft["t"]) == 'T38':
                    logger.debug(aircraft['r'] + " is about to be updated or created...")
                    Acft, created = ActiveAircraft.objects.get_or_create(
                        tailNumber=aircraft["r"][-3:] #,
                    )

                    Acft.callSign=aircraft["flight"]
                    if "SMAL" in Acft.callSign:
                        Acft.solo = True
                    Acft.aircraftType=aircraft['t']
                    #formation=aircraft[""],                need form callsign db
                    Acft.emergency=False if aircraft["emergency"] == "none" else True
                    Acft.alt_baro=aircraft['alt_baro']
                    Acft.groundSpeed=aircraft['gs']
                    Acft.latitude=aircraft['lat']
                    Acft.longitude=aircraft['lon']
                    Acft.track=aircraft['track']
                    Acft.squawk=aircraft['squawk']
                    Acft.seen=aircraft['seen']
                    Acft.rssi=aircraft['rssi']
                    if Acft.alt_baro == "ground":
                        position = geometry.Point(Acft.latitude, Acft.longitude, 1300)
                    else:
                        position = geometry.Point(Acft.latitude, Acft.longitude, int(Acft.alt_baro))
                    if inPattern(position) and Acft.groundSpeed > 70 and Acft.alt_baro != "ground" and Acft.state != "in pattern":
                        Acft.lastState = Acft.state
                        Acft.state="in pattern"
                        if Acft.lastState == "taxiing":
                            Acft.takeoffTime = timezone.now()
                    elif inPattern(position) and Acft.groundSpeed < 70 and Acft.state != "taxiing" and (Acft.alt_baro == "ground" or (int(Acft.alt_baro) >= 1200 and int(Acft.alt_baro < 1350))):
                        Acft.lastState = Acft.state
                        Acft.state="taxiing"
                        if Acft.lastState == "in pattern":
                            Acft.landTime = timezone.now()
                    elif inPattern(position) == False and Acft.state != "off station":
                        Acft.lastState = Acft.state
                        Acft.state="off station" 
                    Acft.timestamp=timezone.now()
                    Acft.save()
                    logger.debug("Success!")   
                    updatedAircraftList.append(Acft.tailNumber)         

            except KeyError as e:
                logger.debug('KeyError in aircraft ' + str(e) + "; however, this is ok.")

        aircraftNotUpdated = getAircraftNotUpdated(updatedAircraftList)
        logger.info('aircraft not updated: ' + str(aircraftNotUpdated))

# TODO NEED TO THOROUGHLY TEST THE LOGIC ABOVE AND BELOW THIS LINE. STATE TRANSITIONS ARE CRITICAL TO GET RIGHT. 

        if aircraftNotUpdated is not None:
            for Acft in aircraftNotUpdated:
                # if Acft.timestamp or Acft.landTime or Acft.state or Acft.lastState is None:
                #     continue
                if Acft.timestamp is not None and (timezone.now() - Acft.timestamp).total_seconds() > 120: 
                    if Acft.landTime == None and Acft.state != "lost signal":
                        Acft.lastState = Acft.state
                        Acft.state = "lost signal"
                        Acft.save()
                    elif Acft.landTime != None and Acft.state != "completed sortie":
                        Acft.lastState = Acft.state
                        Acft.state = "completed sortie"
                        Acft.save()
                if Acft.timestamp is not None and (timezone.now() - Acft.timestamp).total_seconds() > 14400: #4 hrs
                    Acft.lastState = Acft.state
                    Acft.state = "completed sortie"
                    Acft.save()

        killSignal = True
        threads_list = threading.enumerate()
        
        for thread in threads_list:
            if thread.name is parentThreadName and thread.is_alive() is True:
                killSignal = False
        
        if killSignal is False:
            logger.info("ADSB Thread sleeping...")
            time.sleep(1)
            logger.info("ADSB Thread waking up...")

            continue
        else:
            logger.debug("Stopping ADSB Thread")
            os.environ['ENABLE_ADSB'] = 'True'
            return

# patterngeo is: POLYGON Z ((-97.85030679597989 36.34361697636346 356.5965643368178, -97.8519523722311 36.42150409466861 386.7798542217082, -97.8665824662419 36.41770787541027 386.7433724200206, -97.88379406517919 36.42324959552203 405.2495714293286, -97.87599735916334 36.47861104189872 413.0276973875364, -97.95303083318271 36.48381133357203 427.3829198543955, -98.01875560914486 36.34124538321816 413.7861677624667, -97.95432176629562 36.19512333559884 372.9853171169215, -97.87839028617687 36.19511818635721 387.4445295500769, -97.88047829281494 36.27096011513436 386.9419600520378, -97.85030679597989 36.34361697636346 356.5965643368178))
# patterngeo2 is: POLYGON ((36.34274909853927 -97.85060096116348, 36.38501763547715 -97.85340389119733, 36.37083992357469 -97.9199899747725, 36.37083992899921 -97.91998998150338, 36.45457130802796 -97.88064193324243, 36.43822747970118 -97.94454597209545, 36.34029761411401 -98.01874780036422, 36.27950096822119 -97.96044005727545, 36.27950096279858 -97.96044005727501, 36.27950095737597 -97.96044005727457, 36.34274909853927 -97.85060096116348))


def inPattern(position):
    patternCoords = [(36.34274909853927, -97.85060096116348), (36.38501763547715, -97.85340389119733), (36.37083992357469, -97.91998997477251), (36.37083992899921, -97.91998998150338), (36.45457130802796, -97.88064193324243), (36.43822747970118, -97.94454597209545), (36.34029761411401, -98.01874780036422), (36.27950096822119, -97.96044005727545), (36.27950096279858, -97.96044005727501), (36.27950095737597, -97.96044005727457)]
    patternGeo = readKML("./AutoRecorder/static/Autorecorder/kml/RoughPatternPoints.kml") #geometry.Polygon(patternCoords)
    patternGeo2 = geometry.Polygon(patternCoords)
    alt = position.z
    position2d = geometry.Point(position.x, position.y)

    print(position2d)
    
    if position2d.within(patternGeo2) and alt < 5000:
        print("TRUE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return True
    else:
        print("False")
        return False
    

def readKML(file):
    k = kml.KML()
    with open(file, 'rt', encoding='utf-8') as myfile:
        doc = myfile.read().encode('utf-8')
    k.from_string(doc)
    placemarks = []
    parse_placemarks(placemarks, list(k.features()))
    # print(k.to_string(prettyprint=True))
    for placemark in placemarks:
        if placemark.name == "PatternOutline":
            return placemark.geometry
        


def parse_placemarks(target, document):
    for feature in document:
        if isinstance(feature, kml.Placemark):  
           placemark = feature
           target.append(placemark)
    for feature in document:
        if isinstance(feature, kml.Folder):
            parse_placemarks(target, list(feature.features()))
        if isinstance(feature, kml.Document):
           parse_placemarks(target, list(feature.features()))



def getAircraftNotUpdated(updatedAircraftList):
    from AutoRecorder.models import ActiveAircraft
    return ActiveAircraft.objects.exclude(tailNumber__in=updatedAircraftList)
