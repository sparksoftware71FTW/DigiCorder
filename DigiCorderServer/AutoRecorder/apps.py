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
        #Also! This thread WILL interact with the database specified in settings.py... NOT a testing db.
        #Make sure we've got only one background thread running...
        enable_adsb = os.environ.get('ENABLE_ADSB') 
        if enable_adsb == 'False' or enable_adsb == None:
            return
        os.environ['ENABLE_ADSB'] = 'False'
        threadName = threading.current_thread().name
        logger.debug("ready() thread is: " + threadName)
        ADSBThread = threading.Thread(target=adsbThread, args=(threadName,), name='ADSBThread')
        MessageThread = threading.Thread(target=messageThread, args=(1, threadName,), name='ADSBThread')
        ADSBThread.start()
        MessageThread.start()


def messageThread(freq, parentThreadName):
    from AutoRecorder.models import Trigger
    while True:
        trigger, created = Trigger.objects.get_or_create(id=1)
        trigger.sendAllMessages = True
        trigger.save()

        killSignal = True
        threads_list = threading.enumerate()
        
        for thread in threads_list:
            if thread.name is parentThreadName and thread.is_alive() is True:
                killSignal = False
        
        if killSignal is False:
            logger.info("Message Thread sleeping...")
            time.sleep(freq)
            logger.info("Message Thread waking up...")

            continue
        else:
            logger.debug("Stopping Message Thread")
            os.environ['ENABLE_ADSB'] = 'True'
            return

            
def adsbThread(parentThreadName):
    logger.info("Starting ADSB Thread")
    import http.client
    import json
    from AutoRecorder.models import ActiveAircraft, NextTakeoffData, Runway
    import time

    conn = http.client.HTTPSConnection("adsbexchange-com1.p.rapidapi.com")

    headers = {
        'X-RapidAPI-Key': "e7a36b9597msh0954cc7e057677dp160f6fjsn5e333eceedc4",
        'X-RapidAPI-Host': "adsbexchange-com1.p.rapidapi.com"
        }

    # New pattern logic:
    # If any aircraft is in a pattern, add it to active aircraft for displaying
    # Once non-T1/T6/T38 aircraft depart the pattern, delete from active aircraft

    eastsidePatternPolygon = getKMLplacemark("./AutoRecorder/static/Autorecorder/kml/RoughPatternPoints.kml", "Eastside")
    shoehornPatternPolygon = getKMLplacemark("./AutoRecorder/static/Autorecorder/kml/RoughPatternPoints.kml", "Shoehorn")
    patterns = [eastsidePatternPolygon, shoehornPatternPolygon]

    KEND35L = Runway.objects.filter(name='KEND 17R/35L')
    KEND17L = Runway.objects.filter(name='KEND 17L/35R')

    while True:
        logger.info("Requesting ADSB Data...")
        conn.request("GET", "/v2/lat/36.3393/lon/-97.9131/dist/250/", headers=headers)
        res = conn.getresponse()
        data = res.read()
        jsondata = json.loads(data)
        updatedAircraftList = []
        updatedAircraftObjects = [] 

        obj = time.gmtime(0)
        epoch = time.asctime(obj)

        curr_time4 = round(time.time()*1000)
        
        #activeAircraftObjects = {ActiveAircraft.tailNumber: ActiveAircraft for ActiveAircraft in ActiveAircraft.objects.all()}

        curr_time5 = round(time.time()*1000)
        print("Hack 0: it took this long to load all objects initially: ", curr_time5-curr_time4)


        for aircraft in jsondata['ac']: #ac is aircraft in the database 
            try:
                position = getPosition(aircraft)
                if str(aircraft["t"]) == 'TEX2' or str(aircraft["t"]) == 'T38' or inPattern(position, patterns):
                    logger.debug(aircraft['r'] + " is about to be updated or created...")

                    curr_time = round(time.time()*1000)
                    print("Hack 1: Milliseconds since epoch:",curr_time)

                    Acft, created = ActiveAircraft.objects.get_or_create(
                       tailNumber= aircraft["r"][:-3] + "--" + aircraft["r"][-3:]
                    )

                    curr_time2 = round(time.time()*1000)
                    print("Hack 2: get_or_create took:", curr_time2 - curr_time)

                    # try:
                    #     Acft = activeAircraftObjects[aircraft["r"][:-3] + "--" + aircraft["r"][-3:]]
                    # except KeyError as e:
                    #     Acft = ActiveAircraft.objects.create(tailNumber=aircraft["r"][:-3] + "--" + aircraft["r"][-3:])
                    #     logger.debug('KeyError in aircraft ' + str(e) + "; however, this is ok.")


                    curr_time3 = round(time.time()*1000)
                    print("Hack 3: dict lookup or creation took:", curr_time3 - curr_time2)


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
                    if inPattern(position, patterns) and Acft.groundSpeed > 70 and Acft.alt_baro != "ground" and Acft.state != "in pattern": # TODO: test removing ground to fix T-38 bug
                        Acft.lastState = Acft.state
                        Acft.state="in pattern"
                        Acft.substate=setSubstate(position, Acft.state, eastsidePatternPolygon, shoehornPatternPolygon)
                        if Acft.lastState == "taxiing" or (Acft.lastState == None and int(Acft.alt_baro) >= 1000 and int(Acft.alt_baro) < 1600):
                            Acft.takeoffTime = timezone.now()
                            match Acft.substate:
                                case 'shoehorn':
                                    nextTOData = NextTakeoffData.objects.filter(runway = KEND35L)
                                    Acft.solo = nextTOData.solo
                                    Acft.formationX2 = nextTOData.formationX2
                                    Acft.formationX4 = nextTOData.formationX4
                                    resetNextTakeoffData(nextTOData)
                                    logger.info("Next T/O Data applied!!!!!!!!!!!!")
                                case 'eastside':
                                    nextTOData = NextTakeoffData.objects.filter(runway = KEND17L)
                                    Acft.solo = nextTOData.solo
                                    Acft.formationX2 = nextTOData.formationX2
                                    Acft.formationX4 = nextTOData.formationX4
                                    resetNextTakeoffData(nextTOData)
                                    logger.info("Next T/O Data applied!!!!!!!!!!!!")
                                case other:
                                    logger.info("No runway found with recent aircraft's T/O")
                    elif inPattern(position, patterns) and Acft.groundSpeed < 70 and Acft.state != "taxiing" and (Acft.alt_baro == "ground" or (int(Acft.alt_baro) >= 1200 and int(Acft.alt_baro) < 1350)):
                        Acft.lastState = Acft.state
                        Acft.state="taxiing"
                        Acft.substate=setSubstate(position, Acft.state, eastsidePatternPolygon, shoehornPatternPolygon)
                        if Acft.lastState == "in pattern":
                            Acft.landTime = timezone.now()
                    elif inPattern(position, patterns) == False and Acft.state != "off station":
                        Acft.lastState = Acft.state
                        Acft.state="off station"
                        Acft.substate=setSubstate(position, Acft.state, eastsidePatternPolygon, shoehornPatternPolygon) 
                    Acft.timestamp=timezone.now()
                    
                    #form logic 
                    
                    #2ship to 1ship logic 
                    # 
                  #  if Acft.callSign[:-1] == Acft.callSign[:-1] and int(freshAcft.callSign[-1:]) >=  int(freshAcft.callSign[-1:]) - 1 or int(freshAcft.callSign[-1:]) <=  int(freshAcft.callSign[-1:]) + 1   



                    Acft.save()
                    logger.debug("Success!")   
                    updatedAircraftList.append(Acft.tailNumber)     
                    updatedAircraftObjects.append(Acft)

            except KeyError as e:
                logger.debug('KeyError in aircraft ' + str(e) + "; however, this is ok.")

        aircraftNotUpdated = ActiveAircraft.objects.exclude(tailNumber__in=updatedAircraftList) # getAircraftNotUpdated(updatedAircraftList)
        logger.info('aircraft not updated: ' + str(aircraftNotUpdated))

# TODO NEED TO THOROUGHLY TEST THE LOGIC ABOVE AND BELOW THIS LINE. STATE TRANSITIONS ARE CRITICAL TO GET RIGHT. 

        if aircraftNotUpdated is not None:
            for Acft in aircraftNotUpdated:
                # if Acft.timestamp or Acft.landTime or Acft.state or Acft.lastState is None:
                #     continue

                    # Formation logic:
                    # Departure 
                    # Flying Around
                    # Recovery
                    # Four ships
                    # Robust splits and rejoins


                position1 = geometry.Point(0, 0) 
                position2 = geometry.Point(0, 0)

                for freshAcft in updatedAircraftObjects:        #start form logic 
                    # 1ship to 2ship logic 
                    if freshAcft.callSign is not None and Acft.callSign is not None and freshAcft.callSign[:-1] == Acft.callSign[:-1]  and not freshAcft.formationX2 and not Acft.formationX2: 
                        position1 = geometry.Point(Acft.latitude, Acft.longitude)     #find position of 1st jet
                        position2 = geometry.Point(freshAcft.latitude, freshAcft.longitude)  #find position of 2nd jet 

                        if (position2.distance(position1) * 69 < 2) and Acft.groundSpeed < 70 and freshAcft.groundSpeed < 70:           # :)  degrees of lat & long to miles
                            freshAcft.formationX2 == True

                
                if Acft.timestamp is not None and (timezone.now() - Acft.timestamp).total_seconds() > 5: 
                    if Acft.landTime == None and Acft.state != "lost signal":
                        Acft.lastState = Acft.state
                        Acft.state = "lost signal"
                        Acft.substate=Acft.substate=setSubstate(position, Acft.state, eastsidePatternPolygon, shoehornPatternPolygon)
                        Acft.save()
                        logger.info("lost signal")
                    elif Acft.landTime != None and Acft.state != "completed sortie":
                        Acft.lastState = Acft.state
                        Acft.state = "completed sortie"
                        Acft.substate=Acft.substate=setSubstate(position, Acft.state, eastsidePatternPolygon, shoehornPatternPolygon)
                        Acft.save()
                        logger.info("completed sortie")
                if Acft.timestamp is not None and (timezone.now() - Acft.timestamp).total_seconds() > 14400: #4 hrs
                    Acft.lastState = Acft.state
                    Acft.state = "completed sortie"
                    Acft.substate=Acft.substate=setSubstate(position, Acft.state, eastsidePatternPolygon, shoehornPatternPolygon)
                    Acft.save()
                    logger.info("completed sortie")

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


def inPattern(position, patterns):
    alt = position.z
    position2d = geometry.Point(position.x, position.y)  
    for pattern in patterns:
        if position2d.within(pattern) and alt < 4600:
            return True
        else:
            continue
    return False


def getKMLplacemark(file, placemarkName):
    k = kml.KML()
    with open(file, 'rt', encoding='utf-8') as myfile:
        doc = myfile.read().encode('utf-8')
    k.from_string(doc)
    placemarks = []
    parse_placemarks(placemarks, list(k.features()))
    # print(k.to_string(prettyprint=True))
    for placemark in placemarks:
        if placemark.name == placemarkName:
            return swapLatLong(placemark.geometry)


def swapLatLong(polygon):
    coordList = list(polygon.exterior.coords)
    swappedCoordList = []
    for point in coordList:
        newPoint = point[1], point[0]
        swappedCoordList.append(newPoint)
    polygon = geometry.Polygon(swappedCoordList)
    return polygon


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


def getPosition(aircraft):
    if aircraft["alt_baro"] == "ground":
        position = geometry.Point(aircraft["lat"], aircraft["lon"], 1300)
    else:
        position = geometry.Point(aircraft["lat"], aircraft["lon"], int(aircraft["alt_baro"]))
    return position


def setSubstate(position, state, eastside, shoehorn):
    if position.within(eastside) and state == "in pattern":
        return "eastside"
    elif position.within(shoehorn) and state == "in pattern":
        return "shoehorn"
    else:
        return "null"

def resetNextTakeoffData(nextTOData):
    nextTOData.solo = False
    nextTOData.formationX2 = False
    nextTOData.formationX4 = False 
        