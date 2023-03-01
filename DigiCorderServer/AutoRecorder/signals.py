import json
import os
import threading
import asyncio
import time
import json
import math 
import websocket
import traceback
from channels import layers
from django.utils import timezone
from django.utils.timezone import timedelta
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save, m2m_changed
from django.db.models import Q
from django.dispatch import receiver
from django.core import serializers
from django.contrib.auth.models import Group, User
from shapely import geometry
from fastkml import kml


from .models import CommsControl, ActiveAircraft, ActiveAircraftManager, CompletedSortie, Message, Trigger, NextTakeoffData, Runway, RunwayManager, Airfield, UserDisplayExtra

import logging
logger = logging.getLogger(__name__)



LOST_SIGNAL_TIME_THRESHOLD_SECONDS = 5
LOST_SIGNAL_TO_COMPLETED_SORTIE_TIME_THRESHOLD_HOURS = 4

global jsondata 
jsondata = {
    "ac": [] #add/remove aircraft to list here
} # dictionary...
global mutex 
mutex = threading.Lock()

global USAircraft 
USAircraft = {}
with open("./AutoRecorder/static/AutoRecorder/USAaircraft.json") as acftFile:
    USAircraft = json.load(acftFile)


global numUnknownAcft
numUnknownAcft = 0 # global variable to keep track of how many unknown aircraft we've seen that are not in USAircraft.json


@receiver(post_save, sender=ActiveAircraft, dispatch_uid="log_completed_flight")
def log_completed_flight(sender, instance, created, **kwargs):
    if instance.state == "completed sortie":
        #ActiveAircraft.objects.get(pk=instance.tailNumber)
        justLandedAcft = CompletedSortie(
        aircraftType = instance.aircraftType,
        tailNumber=instance.tailNumber,
        callSign=instance.callSign,
        takeoffTime=instance.takeoffTime,
        three55Code=instance.three55Code,
        Comments=instance.Comments,
        landTime=instance.landTime,
        solo=instance.solo,
        formationX2=instance.formationX2,
        formationX4=instance.formationX4,
        emergency=instance.emergency,
        natureOfEmergency=instance.natureOfEmergency,
        groundSpeed=instance.groundSpeed,
        latitude=instance.latitude,
        longitude=instance.longitude,
        alt_baro=instance.alt_baro,
        alt_geom=instance.alt_geom,
        track=instance.track,
        squawk=instance.squawk,
        seen=instance.seen,
        rssi=instance.rssi,
        state=instance.state,
        lastState = instance.lastState,
        timestamp = instance.timestamp,
        formTimestamp = instance.formTimestamp,
        substate = instance.substate
        )
        justLandedAcft.save()
        instance.delete()
        logger.info("Active -> Completed Transition Occured")


@receiver(post_save, sender=NextTakeoffData, dispatch_uid="nextTODisplayUpdate")
def nextTODisplayUpdate(sender, instance, created, **kwargs):

    nextTOMessages = get_next_takeoff_update_messages()
    
    print("Trigger success")

    for msg in nextTOMessages:
        if msg['runway'] == instance.runway.name:
            channel_layer = layers.get_channel_layer()
            async_to_sync(channel_layer.group_send)(
            'test',
                {
                    'type':'nextTOMessage',
                    'runway':msg['runway'],
                    'data':msg        }
            )

@receiver(post_save, sender=Trigger, dispatch_uid="displayActiveAircraft")
def displayActiveAircraft(sender, instance, created, **kwargs):

    channel_layer = layers.get_channel_layer()

    for runway in Runway.objects.all():
        rwyMessage, rwyMetaData = ActiveAircraftManager.get_Acft_queryset_update_message(runway)
        async_to_sync(channel_layer.group_send)(
        'test',
            {
                'type': 'rwyUpdate',
                'runway': runway.name,
                'message': rwyMessage,
                'meta': rwyMetaData
            }
        )



@receiver(m2m_changed, sender=User.groups.through, dispatch_uid="createUserExtras")
def createUserDisplayExtras(sender, instance, action, reverse, **kwargs):

    userGroups = instance.groups.all()
    airfields = []
    for group in userGroups:
        if hasattr(group, 'airfield'):
            airfields.append(group.airfield)
    for airfield in airfields:
        for runway in Runway.objects.filter(airfield=airfield):
            userDisplayExtra, fresh = UserDisplayExtra.objects.get_or_create(runway=runway, user=instance)
            if fresh:
                userDisplayExtra.save()


@receiver(post_save, sender=Airfield, dispatch_uid="createUserGroupForEachAirfield")
def createUserGroupForEachAirfield(sender, instance, created, **kwargs):
    airfieldGroup, created = Group.objects.get_or_create(name=instance.FAAcode)
    if created:
        logger.info("Created user group for airfield: " + airfieldGroup.name)
        instance.userGroup = airfieldGroup
        instance.save()


@receiver(post_save, sender=Runway, dispatch_uid="addRunwayDependencies")
def createRunwayDependencies(sender, instance, created, **kwargs): 

    if created:
        nextTOdata = NextTakeoffData.objects.create(runway=instance,)
        nextTOdata.save()

        airfieldUserGroup = Group.objects.get(name=instance.airfield.FAAcode)
        for user in airfieldUserGroup.user_set.all():
            userDisplayExtras = UserDisplayExtra.objects.create(user=user, runway=instance)
            userDisplayExtras.save()

    
global killSignals
killSignals = {}


@receiver(post_save, sender=CommsControl, dispatch_uid="adsbCommsControl")
def adsbCommsControl(sender, instance, created, **kwargs): 

    logger.info("Comms Control signal function running...")


    # TODO: make sure we spawn or kill threads in accordance with the boolean values of the comms control object
    # rework this funcition to get the commscontrol model and ask "did the admin just turn off the one of the three comms managment thread boolians"
    threadList = threading.enumerate()
    threadNameList = []
    for thread in threadList:
        threadNameList.append(thread.name)
        if thread.name == 'CommsTestThread' and instance.commsManagementThreadStatus is False:
            killSignals['CommsTestThread'] = False
            logger.info("Comms Management Thread is about to die")

        if thread.name == 'ADSBProcessingThread' and instance.ADSBProcessingThreadStatus is False:
            killSignals['ADSBProcessingThread'] = False
            logger.info("ADSB Processing Thread is about to die")      

        if thread.name == 'MessageThread' and instance.MessageThreadStatus is False:
            killSignals['MessageThread'] = False
            logger.info("Message Thread is about to die")

#spawn one and only one of the specificed thread
#if in the comms controls model, any of the boolians are true, we want to spawn each of the specified threads. If the thread is already running, we don't want to spawn another one.
# if the thread is not running, we want to spawn it.
# in these if statements do not look for the thread name in the killSignals dict, because we want to spawn the thread if it is not running, even if it is in the killSignals dict

    if instance.CommsManagementThreadStatus is True and threadNameList is not None and 'CommsManagementThread' not in threadNameList:
        CommsManagementThread = threading.Thread(target=commsManagementThread, args=(threading.current_thread().name,), name='CommsManagementThread')
        killSignals['CommsManagementThread'] = True
        CommsManagementThread.start()
        logger.info("Comms Management Thread is alive")
#do the same thing for the other two threads
    if instance.ADSBProcessingThreadStatus is True and threadNameList is not None and 'ADSBProcessingThread' not in threadNameList:
        ADSBProcessingThread = threading.Thread(target=adsbProcessing, args=(threading.current_thread().name,), name="ADSBProcessingThread")
        killSignals['ADSBProcessingThread'] = True
        ADSBProcessingThread.start()
        logger.info("ADSB Processing Thread is alive")

    if instance.MessageThreadStatus is True and threadNameList is not None and 'MessageThread' not in threadNameList:
        MessageThread = threading.Thread(target=messageThread, args=(.01, threading.current_thread().name,), name='MessageThread')
        killSignals['MessageThread'] = True
        MessageThread.start()
        logger.info("Message Thread is alive")
               
    
    #
    enable_adsb = os.environ.get('ENABLE_ADSB') 
    if enable_adsb == 'False' or enable_adsb == None:
            return
    os.environ['ENABLE_ADSB'] = 'False'



    # threadName = threading.current_thread().name
    # logger.debug("signals thread is: " + threadName)
    # MessageThread = threading.Thread(target=messageThread, args=(.2, threadName,), name='MessageThread')
    # ADSBProcessingThread = threading.Thread(target=adsbProcessing, args=(threadName,), name="ADSBProcessingThread")
    # # AdsbExchangeCommsThread = threading.Thread(target=adsbExchangeCommsThread, args=(threadName, 36.3393, -97.9131, 250))
    # # StratuxCommsThread = threading.Thread(target=stratuxCommsThread, name='StratuxCommsThread')
    # CommsTestThread = threading.Thread(target=commsTestThread, args=(threadName,), name="CommsTestThread")
    # MessageThread.start()
    # #CommsTestThread.start()
    # # StratuxCommsThread.start()
    # # AdsbExchangeCommsThread.start()
    # ADSBProcessingThread.start()
    # CommsManagementThread = threading.Thread(target=commsManagementThread, args=(threadName,), name="CommsManagementThread")
    # CommsManagementThread.start()
    print(threading.enumerate())

 


#@receiver(post_save, sender=Runway, dispatch_uid="createUserGroupForEachRunway")
# def createUserGroupForEachRunway(sender, instance, created, **kwargs):
#     runwayGroup, created = Group.objects.get_or_create(name=instance.name)
#     if created:
#         logger.info("Created user group for runway: " + runwayGroup.name)


def get_ActiveAircraft_queryset():
    """
    Return all active aircraft
    """
    #Question.objects.filter(pub_date__lte=timezone.now())
    return ActiveAircraft.objects.all().order_by('tailNumber')


def get_Message_queryset():
    """
    Return all messages
    """
    #Question.objects.filter(pub_date__lte=timezone.now())
    return Message.objects

def get_next_takeoff_update_messages():
    nextTOquery = NextTakeoffData.objects.all()
    nextTOMessages = []
    for entry in json.loads(serializers.serialize('json', nextTOquery)):
        nextTOMessages.append(
            entry['fields']
        )
    return nextTOMessages



###############################OLD apps.py Functions:#################################


def messageThread(freq, parentThreadName):
    from AutoRecorder.models import Trigger
    while True:
        trigger, created = Trigger.objects.get_or_create(id=1)
        trigger.sendAllMessages = True
        trigger.save()

        keyboardKillSignal = True
        threads_list = []

        for thread in threading.enumerate():
            threads_list.append(thread.name)

        if threads_list.__contains__('django-main-thread'):
            keyboardKillSignal = True

        else:
            keyboardKillSignal = False
        
        if killSignals['MessageThread'] is False or keyboardKillSignal is False:
            logger.info("Message Thread about to die...")
            os.environ['ENABLE_ADSB'] = 'True'
            return
        else:
            # logger.info("Message Thread sleeping...")
            time.sleep(freq)
            logger.info("Message Thread waking up...")
            continue




def adsbProcessing(parentThreadName):

    logger.info("Starting ADSB Processing Thread")
    import http.client
    import json
    from AutoRecorder.models import ActiveAircraft, NextTakeoffData, Airfield, AircraftType, Runway, AircraftType, Callsign
    import time
    import copy
    from fuzzywuzzy import fuzz

    # New pattern logic:
    # If any aircraft is in a pattern, add it to active aircraft for displaying
    # Once non-T1/T6/T38 aircraft depart the pattern, delete from active aircraft
 
    
    patternDict = {}
    for runway in Runway.objects.all():
        patternPolygon = getKMLplacemark("./AutoRecorder" + runway.kmlPatternFile.url, runway.patternName)
        patternDict[runway.patternName] = (patternPolygon, runway.patternAltitudeCeiling, runway.airfield.fieldElevation, runway.patternName)        

    soloCallsignList = []
    for callsign in Callsign.objects.filter(type='solo'):
        soloCallsignList.append(callsign.callsign)

    i = 0
    while True:
        logger.info("Requesting ADSB Data...")

        newData = {
            "ac": [] #add/remove aircraft to list here
        } # dictionary...
        with mutex:
            newData = copy.deepcopy(jsondata)

        # logfile = open(r"./AutoRecorder/testFiles/ADSBsnapshot" + str(i) + ".json", "w")
        # logfile.write(json.dumps(jsondata))
        # logfile.close
        # i+=1

        updatedAircraftList = []
        updatedAircraftObjects = [] 

        activeAircraftObjects = ActiveAircraft.objects.all()
        activeAircraftDict = {ActiveAircraft.tailNumber: ActiveAircraft for ActiveAircraft in activeAircraftObjects} #load a dictionary of active aircraft objects; this is MUCH faster than querying the database for each aircraft

        aircraftTypes = AircraftType.objects.all()
        aircraftTypeDict = {AircraftType.aircraftType: AircraftType for AircraftType in aircraftTypes} #load a dictionary of aircraft types; this is faster than querying the database for each aircraft type

        activeFormationX2 = list(activeAircraftObjects.filter(formationX2=True)) #list of active aircraft that are 2-ships
        activeFormationX4 = list(activeAircraftObjects.filter(formationX4=True)) #list of active aircraft that are 4-ships

        logger.debug(newData)
        for aircraft in newData['ac']: #iterate through all aircraft in the latest ADSB data


            try:
                position = getPosition(aircraft)
                if str(aircraft["t"]) in aircraftTypeDict or inPattern(position, patternDict):
                    logger.debug(aircraft['r'] + " is about to be updated or created...")

                    try:
                        Acft = activeAircraftDict[aircraft["r"][:-3] + "--" + aircraft["r"][-3:]]
                    except KeyError as e:
                        Acft = ActiveAircraft.objects.create(tailNumber=aircraft["r"][:-3] + "--" + aircraft["r"][-3:])
                        logger.info('KeyError in aircraft ' + str(e) + "; however, this is ok. We just need to create a new aircraft")

                    
                    try:
                        Acft.aircraftType = aircraftTypeDict[aircraft["t"]]
                    except KeyError as e:
                        newType = AircraftType.objects.create(aircraftType=aircraft["t"])
                        aircraftTypeDict[aircraft["t"]] = newType
                        Acft.aircraftType = newType
                        logger.info('KeyError in aircraft ' + str(e) + "; however, this is ok. We just need to create a new aircraft TYPE")


                    if Acft.callSign is None and aircraft["flight"] == "":
                        Acft.callSign = ''

                    elif Acft.callSign is not None and Acft.callSign != '' and aircraft['flight'] == "":
                        Acft.callSign = Acft.callSign

                    else:
                        Acft.callSign = aircraft["flight"]

                    for callsign in soloCallsignList:
                        if fuzz.ratio(Acft.callSign, callsign) >= 80:
                            Acft.solo = True
                    #formation=aircraft[""],                need form callsign db?
                    # Acft.emergency=False if aircraft["emergency"] == "none" else True
                    Acft.alt_baro=aircraft['alt_baro']
                    Acft.groundSpeed=aircraft['gs']
                    Acft.latitude=aircraft['lat']
                    Acft.longitude=aircraft['lon']
                    Acft.track=aircraft['track']
                    Acft.squawk=aircraft['squawk']
                    Acft.emergency = True if Acft.squawk == "7700" or Acft.squawk == "7600" or Acft.squawk == "7500" else False
                    Acft.seen=aircraft['seen']
                    Acft.rssi=aircraft['rssi']
                    if Acft.alt_baro == "ground":
                        position = geometry.Point(Acft.latitude, Acft.longitude, 0)
                    else:
                        position = geometry.Point(Acft.latitude, Acft.longitude, int(Acft.alt_baro))
                    # the in pattern criteria is that the aircraft is in a pattern, has a groundspeed greater than the full stop threshold speed, and is not on the ground or already in a pattern
                    if inPattern(position, patternDict) and Acft.groundSpeed > Acft.aircraftType.fullStopThresholdSpeed and Acft.alt_baro != "ground" and Acft.state != "in pattern": 
                        Acft.lastState = Acft.state
                        Acft.state="in pattern"
                        Acft.substate=setSubstate(position, Acft.state, patternDict)

                        # the takeoff criteria is as follows: the aircraft either transitioned from taxiing to airborne in a pattern, or has a groundspeed greater than the full stop threshold speed and is airborne in a pattern and this is the first we've seen it
                        if Acft.lastState == "taxiing" or (Acft.lastState == None and int(Acft.alt_baro) < int(patternDict[Acft.substate][2] + 200)): # field elevation is the [2]nd element in each tuple within patternDict - this hard-codes a 200 ft threshold to deal with low-altitude adsb signal loss
                            Acft.takeoffTime = timezone.now()
                            try:
                                nextTOData = NextTakeoffData.objects.get(runway__patternName = Acft.substate)
                                Acft.solo = nextTOData.solo
                                Acft.formationX2 = nextTOData.formationX2
                                Acft.formationX4 = nextTOData.formationX4
                                resetNextTakeoffData(nextTOData)
                                logger.info("Next T/O Data applied!")
                            except:
                                logger.error("Error processing next T/O data for acft with substate: " + Acft.substate)
                                logger.error(traceback.format_exc())
                    # otherwise, if the aircraft is in the pattern, is below 150 ft, and is also below the full stop threshold speed, it is taxiing
                    elif inPattern(position, patternDict) and Acft.groundSpeed < Acft.aircraftType.fullStopThresholdSpeed and Acft.state != "taxiing" and (Acft.alt_baro == "ground" or int(Acft.alt_baro) < int(patternDict[Acft.substate][2] + 150)):
                        Acft.lastState = Acft.state
                        Acft.state="taxiing"
                        Acft.substate=setSubstate(position, Acft.state, patternDict)
                        if Acft.lastState == "in pattern":
                            Acft.landTime = timezone.now()
                    # finally, the off station criteria is that the aircraft is not in a pattern and is not on the ground
                    elif inPattern(position, patternDict) == False and Acft.state != "off station":
                        Acft.lastState = Acft.state
                        Acft.state="off station"
                        Acft.substate=setSubstate(position, Acft.state, patternDict) 
                    Acft.timestamp=timezone.now()
                    
                   #form logic 
                    
                #2ship to 1ship logic 
                # Check if this aircraft is splitting from a 2 ship nearby
                    closestFormation = None
                    closestFormationDistance = None

                    for formAcft in activeFormationX2: # iterate through each aircraft in the active formation list

                        formAcftPosition = geometry.Point(0,0,0)
                        if formAcft.alt_baro == "ground":
                            formAcftPosition = geometry.Point(formAcft.latitude, formAcft.longitude, 0)
                        else:
                            formAcftPosition = geometry.Point(formAcft.latitude, formAcft.longitude, int(formAcft.alt_baro))

                        if Acft.callSign == '':
                            break
                        if formAcft.callSign == '': # deal with blank callsigns
                            continue

                        # if this aircraft was marked as the wingman of the formation, and it is now transmitting ADSB, then the formation is over
                        if Acft.tailNumber == formAcft.wingman: 
                            logger.info('Wingman started sqwuaking')
                            formAcft.formationX2 = False 
                            formAcft.formTimestamp = timezone.now()
                            Acft.formTimestamp = timezone.now()
                            formAcft.save()
                            Acft.save()  

                        # check callsigns (excluding the last character) to see if they match
                        elif  Acft.callSign[:-1] == formAcft.callSign[:-1] and Acft.formationX2 is False:

                            # check if the last digit is plus or minus 1 of the other aircraft
                            if int(Acft.callSign[-1:]) >=  int(formAcft.callSign[-1:]) - 1 or int(Acft.callSign[-1:]) <=  int(formAcft.callSign[-1:]) + 1:
                                distance = distance(formAcftPosition[0],formAcftPosition[1],formAcftPosition[2],position[0],position[1],position[2]) #distance calculated by Haversine formula
                                
                                # check if the distance between the two aircraft is less than the threshold, and both aircraft are moving faster than the full stop threshold speed (to ensure they are not on the ground)
                                if (distance <= Acft.aircraftType.formationDistThreshold) and Acft.groundSpeed > Acft.aircraftType.fullStopThresholdSpeed and formAcft.groundSpeed > formAcft.aircraftType.fullStopThresholdSpeed:

                                    # if the last state of either aircraft is None (meaning they are just starting to transmit ADSB for the first time on this flight), or if the last state of both aircraft is "lost signal" and the time difference between the two aircraft is less than the threshold, then they are a splitting formation
                                    if (Acft.lastState is None and Acft.takeoffTime is None) or (Acft.lastState is not None and Acft.formTimestamp is not None and formAcft.formTimestamp is not None) and (Acft.lastState == "lost signal" and abs(Acft.formTimestamp - formAcft.formTimestamp) <= timedelta(seconds=Acft.aircraftType.formationLostSignalTimeThreshold)):
                                        if closestFormation is None or distance < closestFormationDistance:
                                            closestFormation = formAcft # track the closest formation to the current formation aircraft - in the context of the loop, this will be the closest eligible formation to the current splitting aircraft
                                            closestFormationDistance = distance 

                    # if the closest formation is not None, then the current aircraft is splitting from that formation
                    if closestFormation is not None:
                        #     if form.tailNumber == closestFormation.tailNumber:
                        activeFormationX2.remove(closestFormation)
                        closestFormation.formationX2 = False
                        closestFormation.formTimestamp = timezone.now()
                        Acft.formTimestamp = timezone.now()
                        closestFormation.save()
                        
                    #4 -> 2-ship logic

                    closestFormation = None
                    closestFormationDistance = None

                    for formAcft in activeFormationX4:

                        formAcftPosition = geometry.Point(0,0,0)
                        if formAcft.alt_baro == "ground":
                            formAcftPosition = geometry.Point(formAcft.latitude, formAcft.longitude, 0)
                        else:
                            formAcftPosition = geometry.Point(formAcft.latitude, formAcft.longitude, int(formAcft.alt_baro))

                        if Acft.callSign == '':
                            break
                        if formAcft.callSign == '':
                            continue
                        if  Acft.callSign[:-1] == formAcft.callSign[:-1] and Acft.formationX4 is False:
                            if int(Acft.callSign[-1:]) >=  int(formAcft.callSign[-1:]) - 3 or int(Acft.callSign[-1:]) <=  int(formAcft.callSign[-1:]) + 3:
                                distance = position.distance(formAcftPosition) * 69
                                if (distance <= Acft.aircraftType.formationDistThreshold) and Acft.groundSpeed > Acft.aircraftType.fullStopThresholdSpeed and formAcft.groundSpeed > formAcft.aircraftType.fullStopThresholdSpeed:
                                    if (Acft.lastState is None and Acft.takeoffTime is None) or (Acft.lastState is not None and Acft.formTimestamp is not None and formAcft.formTimestamp is not None) and (Acft.lastState == "lost signal" and abs(Acft.formTimestamp - formAcft.formTimestamp) <= timedelta(seconds=Acft.aircraftType.formationLostSignalTimeThreshold)):
                                        if closestFormation is None or distance < closestFormationDistance:
                                            closestFormation = formAcft
                                            closestFormationDistance = distance

                    if closestFormation is not None:
                        #     if form.tailNumber == closestFormation.tailNumber:
                        activeFormationX2.remove(closestFormation)
                        closestFormation.formationX2 = False
                        closestFormation.formTimestamp = timezone.now()
                        Acft.formTimestamp = timezone.now()
                        closestFormation.save()

                    Acft.save()
                    logger.debug("Success!, Acft is" + Acft.tailNumber) 
                    updatedAircraftList.append(Acft.tailNumber)     
                    updatedAircraftObjects.append(Acft)

            except KeyError as e:
                logger.error('KeyError in aircraft ' + str(e) + str(aircraft) + "; however, this is probably okay...")
                logger.error(traceback.format_exc())
            except Exception as e:
                logger.error('Error in aircraft ' + str(e) + str(aircraft))
                logger.error(traceback.format_exc())

        try:
            aircraftNotUpdated = ActiveAircraft.objects.exclude(tailNumber__in=updatedAircraftList) # getAircraftNotUpdated(updatedAircraftList)
        # logger.info('aircraft not updated: ' + str(aircraftNotUpdated))

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

    # from geopy.distance import distance
    # from shapely.geometry import Point

    # # Define two points
    # point1 = Point(40.748817, -73.985428)  # New York City
    # point2 = Point(51.507351, -0.127758)  # London

    # # Calculate the distance between the two points
    # distance_km = distance((point1.y, point1.x), (point2.y, point2.x)).km

    # print(distance_km)  # Output: 5571.047657186649

                    position1 = geometry.Point(0, 0) #initialize position1 and position2 to 0,0 
                    position2 = geometry.Point(0, 0)

                    for freshAcft in updatedAircraftObjects:        #start form logic 
                        # 1ship to 2ship logic )

                        if freshAcft.callSign is not None and Acft.callSign is not None and freshAcft.callSign[:-1] == Acft.callSign[:-1]  and not freshAcft.formationX2 and not Acft.formationX2: 
                            position1 = geometry.Point(Acft.latitude, Acft.longitude) if Acft.latitude is not None else geometry.Point(0, 0)    #find position of 1st jet
                            position2 = geometry.Point(freshAcft.latitude, freshAcft.longitude) if freshAcft.latitude is not None else geometry.Point(0, 0)  #find position of 2nd jet 
                            
                            if (position2.distance(position1) * 69 <= Acft.aircraftType.formationDistThreshold) and Acft.groundSpeed > Acft.aircraftType.fullStopThresholdSpeed and freshAcft.groundSpeed > freshAcft.aircraftType.fullStopThresholdSpeed:           # :)  degrees of lat & long to miles Recalc with function above
                                if abs(Acft.timestamp - timezone.now()) <= timedelta(seconds=Acft.aircraftType.formationLostSignalTimeThreshold):
                                    if int(Acft.callSign[-1:]) >=  int(freshAcft.callSign[-1:]) - 1 or int(Acft.callSign[-1:]) <=  int(freshAcft.callSign[-1:]) + 1:
                                        freshAcft.formationX2 = True
                                        freshAcft.formTimestamp = timezone.now()
                                        Acft.formTimestamp = timezone.now()
                                        Acft.wingman= freshAcft.tailNumber
                                        freshAcft.wingman = Acft.tailNumber
                                        freshAcft.save()
                                        Acft.save()

                        # 2 -> 4-ship logic

                        elif freshAcft.callSign is not None and Acft.callSign is not None and freshAcft.callSign[:-1] == Acft.callSign[:-1]  and freshAcft.formationX2 and Acft.formationX2: 
                            position1 = geometry.Point(Acft.latitude, Acft.longitude) if Acft.latitude is not None else geometry.Point(0, 0)    #find position of 1st jet
                            position2 = geometry.Point(freshAcft.latitude, freshAcft.longitude) if freshAcft.latitude is not None else geometry.Point(0, 0)  #find position of 2nd jet 
                            
                            if (position2.distance(position1) * 69 <= Acft.aircraftType.formationDistThreshold) and Acft.groundSpeed > Acft.aircraftType.fullStopThresholdSpeed and freshAcft.groundSpeed > freshAcft.aircraftType.fullStopThresholdSpeed:           # :)  degrees of lat & long to miles
                                if abs(Acft.timestamp - timezone.now()) <= timedelta(seconds=Acft.aircraftType.formationLostSignalTimeThreshold):
                                    if int(Acft.callSign[-1:]) >=  int(freshAcft.callSign[-1:]) - 3 or int(Acft.callSign[-1:]) <=  int(freshAcft.callSign[-1:]) + 3:
                                        freshAcft.formationX4 = True
                                        freshAcft.formTimestamp = timezone.now()
                                        Acft.formTimestamp = timezone.now()
                                        freshAcft.save()
                                        Acft.save()

                    position = geometry.Point(Acft.latitude, Acft.longitude) if Acft.latitude is not None else geometry.Point(0, 0)
                    if Acft.timestamp is not None and (timezone.now() - Acft.timestamp).total_seconds() > LOST_SIGNAL_TIME_THRESHOLD_SECONDS: # 5 sec
                        if Acft.landTime == None and Acft.state != "lost signal":
                            Acft.lastState = Acft.state
                            Acft.state = "lost signal"
                            Acft.substate=Acft.substate=setSubstate(position, Acft.state, patternDict)
                            Acft.save()
                            logger.info("lost signal")
                        elif Acft.landTime != None and Acft.state != "completed sortie":
                            Acft.lastState = Acft.state
                            Acft.state = "completed sortie"
                            Acft.substate=Acft.substate=setSubstate(position, Acft.state, patternDict)
                            Acft.save()
                            logger.info("completed sortie")
                    if Acft.timestamp is not None and (timezone.now() - Acft.timestamp).total_seconds() > LOST_SIGNAL_TO_COMPLETED_SORTIE_TIME_THRESHOLD_HOURS*3600: #4 hrs
                        Acft.lastState = Acft.state
                        Acft.state = "completed sortie"
                        Acft.substate=Acft.substate=setSubstate(position, Acft.state, patternDict)
                        Acft.save()
                        logger.info("completed sortie")
        except Exception as e:
            logger.error(traceback.format_exc())

        keyboardKillSignal = True
        threadNameList = []

        for thread in threading.enumerate():
            threadNameList.append(thread.name)

        if threadNameList.__contains__('django-main-thread'):
            keyboardKillSignal = True

        else:
            keyboardKillSignal = False
        
        if killSignals['ADSBProcessingThread'] is False or keyboardKillSignal is False:
            logger.debug("Stopping ADSB Processing Thread")
            os.environ['ENABLE_ADSB'] = 'True'
            return
        else:
            # logger.info("ADSBProcessingThread sleeping...")
            # time.sleep(0.3)
            # logger.info("ADSBProcessingThread waking up...")
            continue




def commsTestThread(parentThreadName, sourceName):
    import websocket
    import json
    import time
    dummyWebSocket = websocket.WebSocket()

    with open(r"./AutoRecorder/testFiles/Stratux/ADSBsnapshotsLARGE2.json") as logfile:
        data = json.load(logfile)

        for message in data["testData"]:
            # process the next message
            on_message(dummyWebSocket, json.dumps(message))

            # check if the parent thread is still alive or a keyboard killsignal has been sent
            keyboardKillSignal = True
            threadNameList = []

            for thread in threading.enumerate():
                threadNameList.append(thread.name)

            if threadNameList.__contains__('django-main-thread'):
                keyboardKillSignal = True

            else:
                keyboardKillSignal = False
            
            if killSignals[sourceName] is False or keyboardKillSignal is False:
                logger.debug("Stopping Comms Test Thread")
                os.environ['ENABLE_ADSB'] = 'True'
                return
            else:
                # logger.info("Comms Test Thread sleeping...")
                # sleep for 20ms in order to approximate real-time messages
                # time.sleep(0.01)
                # logger.info("Comms Test Thread waking up...")
                continue




def stratuxCommsThread(address, threadName):
    wsapp = websocket.WebSocketApp(address, on_message=on_message,)
    logger.info("Connecting to Stratux now...")
    
    # Start the WebSocket connection in a new thread
    ws_thread = threading.Thread(target=wsapp.run_forever)
    ws_thread.start()

    # check if the parent thread is still alive or a keyboard killSignal has been sent
    keyboardKillSignal = True
    threadNameList = []

    for thread in threading.enumerate():
        threadNameList.append(thread.name)

    if threadNameList.__contains__('django-main-thread'):
        keyboardKillSignal = True

    else:
        keyboardKillSignal = False

    # Kill the thread if we receive a kill signal
    while ws_thread.is_alive():
        # Check for a kill signal here
        if killSignals[threadName] is False or keyboardKillSignal is False:
            logger.info("About to kill " + str(threading.current_thread()))
            # Close the WebSocket connection and stop the loop
            wsapp.close()
            break

        # Wait for a short time before checking again
        time.sleep(1)

    # Wait for the thread to finish and clean up resources
    ws_thread.join()


 
def on_message(ws, message):
    # Manipulate message from Stratux format to ADSB Exchange format. See stratux.json in testFiles for comments
    dictMessage = json.loads(message)

    logfile = open(r"./AutoRecorder/testFiles/Stratux/ADSBsnapshotsLARGE" + ".json", "a+")
    logfile.write(json.dumps(dictMessage))
    logfile.close
    
    # Do nothing with signals that don't have a valid position
    if dictMessage['Lat'] == 0 or dictMessage["Lng"] == 0:
        deleteOldAircraft()
        # logger.info("Aircraft " + dictMessage["Tail"] + "not saved since it had a null position")
        return
    reformattedMessage = Stratux_to_ADSBExchangeFormat(message)
    with mutex:
        aggregate(reformattedMessage)
    # with mutex:
        deleteOldAircraft()
        # print(jsondata)

def on_error(ws, error):
    logger.warning(error)

# create an aggregate .json file with all traffic every second infinitely
def aggregate(reformattedMessage):
    reformattedMessage = json.loads(reformattedMessage)
    # print("yeehaw... This should work this time...")
    i = 0
    for acft in jsondata["ac"]:
        # print("entering loop")
        # print("acft is" + str(acft))
        # print("jsondata is: " + str(jsondata))
        # print("reformattedMessage is: " + str(reformattedMessage))
        # print("acft registration is: " + acft["r"])
        # print("reformatted registration is: " + reformattedMessage["r"])
        if acft["r"] == reformattedMessage["r"]:
            # print("!!!!!!!!!!!!!!!!!!!!")
            jsondata['ac'][i] = reformattedMessage
            # print(jsondata)
            return
        i+=1
    # if acft does not currently have an entry in jsondata, then add it
    jsondata["ac"].append(reformattedMessage)
    # print(jsondata)
    return

def deleteOldAircraft():
    # print("this function will delete all acft older than 1min from jsondata")
    
    for acft in jsondata["ac"]:
        # print("made it")
        if acft['seen'] >= 59.0:
            print("ABOUT TO REMOVE " + acft['flight'] + "from jsondata.")
            jsondata["ac"].remove(acft)
            print("REMOVED " + acft['flight'] + "from jsondata.")

        # timestamp = parser.parse(acft["Timestamp"])
        # if (timezone.now() - timestamp).seconds > 60:
        #     jsondata["ac"].remove(acft)
        

def Stratux_to_ADSBExchangeFormat(inputMessage):

    JSONmessage = json.loads(inputMessage) 

    hexKey = hex(JSONmessage['Icao_addr'])[2:].upper()

    acft = {}

    global numUnknownAcft

    try:
        acft = USAircraft[hexKey]

    except KeyError:
        logger.warning("KeyError: Icao_addr not found in USAircraft.json")
        acft = {'r': f"{numUnknownAcft:07d}", 't': 'UNKN', 'f': '00', 'd': 'Unknown Aircraft Type'}
        numUnknownAcft += 1
        USAircraft[hexKey] = acft

    #grab r & t from    USAircraft[hexKey] 
    JSONmessage['r'] = acft["r"]
    JSONmessage['t'] = acft["t"]
    JSONmessage['d'] = acft['d']
    JSONmessage['hex'] = hex(JSONmessage.pop('Icao_addr'))[2:]   # replace 
    JSONmessage['flight'] = JSONmessage.pop('Tail')   # replace "Tail" key with "flight" key 
    JSONmessage['dbFlags'] = JSONmessage['TargetType']
    JSONmessage['alt_baro'] =  "ground" if JSONmessage.pop('OnGround') is True else str(JSONmessage.pop('Alt'))
    JSONmessage['rssi'] = JSONmessage.pop('SignalLevel')
    JSONmessage['squawk'] = JSONmessage.pop('Squawk')
    JSONmessage['lat'] = JSONmessage.pop('Lat')
    JSONmessage['lon'] = JSONmessage.pop('Lng')
    JSONmessage['baro_rate'] = JSONmessage.pop('Vvel')
    JSONmessage['nic'] = JSONmessage.pop('NIC')
    JSONmessage['nac_p'] = JSONmessage.pop('NACp')
    JSONmessage['track'] = JSONmessage.pop('Track')
    JSONmessage['gs'] = JSONmessage.pop('Speed')
    JSONmessage['seen'] = JSONmessage.pop('Age')

    # print(JSONmessage)
    outputJSON = json.dumps(JSONmessage)
    return outputJSON


def adsbExchangeCommsThread(parentThreadName, lat, lon, radius):
    import http.client
    import json
    import time

    conn = http.client.HTTPSConnection("adsbexchange-com1.p.rapidapi.com")

    headers = {
        'X-RapidAPI-Key': "e7a36b9597msh0954cc7e057677dp160f6fjsn5e333eceedc4",
        'X-RapidAPI-Host': "adsbexchange-com1.p.rapidapi.com"
        }

    while True:

        request = "/v2/lat/" + str(lat) + "/lon/" + str(lon) + "/dist/" + str(radius) + "/"
        conn.request("GET", request, headers=headers)
        print(request)
        
        res = conn.getresponse()
        data = res.read()

        with mutex:
            jsondata["ac"] = json.loads(data["ac"])
            # print(jsondata)

        # check if the django main thread is still alive or a keyboard killsignal has been sent
        keyboardKillSignal = True
        threadNameList = []

        for thread in threading.enumerate():
            threadNameList.append(thread.name)

        if threadNameList.__contains__('django-main-thread'):
            keyboardKillSignal = True

        else:
            keyboardKillSignal = False
        
        if killSignals['ADSBExchangeCommsThread'] is False or keyboardKillSignal is False:
            logger.debug("Stopping ADSBExchange Comms Thread")
            os.environ['ENABLE_ADSB'] = 'True'
            return
        else:
            # logger.info("Comms Test Thread sleeping...")
            # sleep for 1s in order to save money on API calls
            time.sleep(1)
            # logger.info("Comms Test Thread waking up...")
            continue



def inPattern(position, patternDict):
    alt = position.z
    position2d = geometry.Point(position.x, position.y)  
    for pattern in patternDict:
        if position2d.within(patternDict[pattern][0]) and alt < patternDict[pattern][1]: #[0] is the geometric shape, [1] is the altitudeCeiling
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


def setSubstate(position, state, patternDict):

    if state=="in pattern" or state=="taxiing" or state=="completed sortie":

        for pattern in patternDict:
            if position.within(patternDict[pattern][0]):
                return patternDict[pattern][3]
    return "null"


def resetNextTakeoffData(nextTOData):
    nextTOData.solo = False
    nextTOData.formationX2 = False
    nextTOData.formationX4 = False 
    nextTOData.save()
        

# CommsManagementThread
def commsManagementThread(parentThreadName):
    """Loop to ADSB sources and make sure status is not inactive
    Every second Monitor and make sure"""

    from AutoRecorder.models import ADSBSource

    while True:

        # Get a list of all active ADSB sources
        adsbSources=ADSBSource.objects.all() 

        # List of all running threads
        threads_list = threading.enumerate()

        for source in adsbSources:
            # Kill any threads if the source is declared inactive
            if source.threadSwitch is False:
                for thread in threads_list:
                    
                    # Check if the thread name matches the source
                    if thread.name == "adsbSourceThread" + str(source.id):
                        
                        # Set the killSignal to false
                        killSignals[thread.name] = False                     
                
            else:
                # Convience variable to not be adding the strings together
                threadName = "adsbSourceThread" + str(source.id)

                # Check if the thread with the source ID exists
                continueSignal = None 
                for thread in threads_list:
                    if thread.name == threadName: 
                        continueSignal = True               

                # If the thread doesn't exist create and start a new thread
                
                if continueSignal is True:
                    continue
                else:
                    CommsThread = threading.Thread(target=adsbSource, args=(parentThreadName, source,), name="adsbSourceThread" + str(source.id))
                    # Set the killSignal to true
                    killSignals[threadName] = True
                    CommsThread.start()
                    print("Starting thread..." + str(CommsThread))
                    print("threads_list is: " + str(threads_list))

                    print(killSignals)


        
        # check if the django main thread is still alive or if it was killed via a keyboard input
        keyboardKillSignal = True
        threadNameList = []

        for thread in threading.enumerate():
            threadNameList.append(thread.name)

        if threadNameList.__contains__('django-main-thread'):
            keyboardKillSignal = True

        else:
            keyboardKillSignal = False
        
        if killSignals['CommsManagementThread'] is False or keyboardKillSignal is False:
            logger.debug("Stopping Comms Management Thread")
            os.environ['ENABLE_ADSB'] = 'True'
            return
        else:
            # logger.info("Comms Management Thread sleeping...")
            # sleep for 1s to not bog down the CPU
            time.sleep(1)
            # logger.info("Comms Management Thread waking up...")
            continue


def adsbSource(parentThreadName, source): #takes new source of ADSB data that was created and put it info on a new thread, make connection, process data, get permission to edit mutex json and insert data.
   
    threadName = "adsbSourceThread" + str(source.id)

    while killSignals[threadName] == True:

        logger.info("Starting " + str(threadName) + " with source type: " + str(source.sourceType))
       
        #-> call stratuxCommThread
        if source.sourceType == 'Local' :
            logger.info("Starting stratuxComms...")
            stratuxCommsThread(source.address, threadName)
        elif source.sourceType == 'Historical':
            commsTestThread(parentThreadName, threadName)
        else :
            adsbExchangeCommsThread(parentThreadName,source.lat,source.lon, source.radius)#partent thread name,lat,long,source radius

        # check if the django main thread is still alive or if it was killed via a keyboard input
        keyboardKillSignal = True
        threadNameList = []

        for thread in threading.enumerate():
            threadNameList.append(thread.name)

        logger.info("threadNameList is: " + str(threadNameList))

        if threadNameList.__contains__('django-main-thread'):
            keyboardKillSignal = True

        else:
            keyboardKillSignal = False
        
        if killSignals[threadName] is False or keyboardKillSignal is False:
            logger.debug("Stopping " + str(threadName))
            os.environ['ENABLE_ADSB'] = 'True'
            return
        else:
            # logger.info("Comms Management Thread sleeping...")
            # sleep for 1s to not bog down the CPU
            time.sleep(1)
            # logger.info("Comms Management Thread waking up...")
            continue
    return


def distance(lat1, lon1, alt1, lat2, lon2, alt2): #Calculates the straing line distance beween 2 points in space. (Lat, Lon, Feet, Lat, Lon, Feet)
    R = 20925721.784777 # radius of the earth in feet
        # convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # calculate the differences between the latitudes and longitudes
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    dalt = alt2 - alt1

    # apply the Haversine formula
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c
    
    # calculate the distance in 3D space
    return (math.sqrt(d ** 2 + dalt ** 2)/5280)

#[<_MainThread(MainThread, started 310004)>, <Thread(MessageThread, started 279932)>, <Thread(CommsTestThread, started 307460)>, <Thread(ADSBProcessingThread, started 301936)>]