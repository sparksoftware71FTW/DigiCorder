import os
import threading
import asyncio
import time
import json
from django.apps import AppConfig
from django.utils.timezone import timedelta
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from shapely import geometry
from fastkml import kml


import logging
logger = logging.getLogger(__name__)

# LOST_SIGNAL_TIME_THRESHOLD_SECONDS = 5
# LOST_SIGNAL_TO_COMPLETED_SORTIE_TIME_THRESHOLD_HOURS = 4

# global jsondata 
# jsondata = {
#     "ac": [] #add/remove aircraft to list here
# } # dictionary...
# global mutex 
# mutex = threading.Lock()

# global USAircraft 
# USAircraft = {}
# with open("./AutoRecorder/static/AutoRecorder/USAaircraft.json") as acftFile:
#     USAircraft = json.load(acftFile)

class AutoRecorderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'AutoRecorder'

    def ready(self):

        from AutoRecorder import signals
        #This is where the background thread will kick off...
        #Also! This thread WILL interact with the database specified in settings.py... NOT a testing db.
        #Make sure we've got only one background thread running...
#         enable_adsb = os.environ.get('ENABLE_ADSB') 
#         if enable_adsb == 'False' or enable_adsb == None:
#             return
#         os.environ['ENABLE_ADSB'] = 'False'
#         threadName = threading.current_thread().name
#         logger.debug("ready() thread is: " + threadName)
#         MessageThread = threading.Thread(target=messageThread, args=(.2, threadName,), name='MessageThread')
#         ADSBProcessingThread = threading.Thread(target=adsbProcessing, args=(threadName,), name="ADSBProcessingThread")
#         # AdsbExchangeCommsThread = threading.Thread(target=adsbExchangeCommsThread, args=(threadName, 36.3393, -97.9131, 250))
#         # StratuxCommsThread = threading.Thread(target=stratuxCommsThread, name='StratuxCommsThread')
#         CommsTestThread = threading.Thread(target=commsTestThread, args=(threadName,), name="CommsTestThread")
#         MessageThread.start()
#         #CommsTestThread.start()
#         # StratuxCommsThread.start()
#         # AdsbExchangeCommsThread.start()
#         ADSBProcessingThread.start()
#         CommsManagment = threading.Thread(target=commsManagment, args=(threadName,), name="CommsManagment")
#         CommsManagment.start()
#         print(threading.enumerate())


# def messageThread(freq, parentThreadName):
#     from AutoRecorder.models import Trigger
#     while True:
#         trigger, created = Trigger.objects.get_or_create(id=1)
#         trigger.sendAllMessages = True
#         trigger.save()

#         killSignal = True
#         threads_list = threading.enumerate()
        
#         for thread in threads_list:
#             if thread.name is parentThreadName and thread.is_alive() is True:
#                 killSignal = False
        
#         if killSignal is False:
#             logger.info("Message Thread sleeping...")
#             time.sleep(freq)
#             logger.info("Message Thread waking up...")

#             continue
#         else:
#             logger.debug("Stopping Message Thread")
#             os.environ['ENABLE_ADSB'] = 'True'
#             return




# def adsbProcessing(parentThreadName):
#     logger.info("Starting ADSB Processing Thread")
#     import http.client
#     import json
#     from AutoRecorder.models import ActiveAircraft, NextTakeoffData, Airfield, AircraftType, Runway, AircraftType, Callsign
#     import time
#     import copy
#     from fuzzywuzzy import fuzz

#     # New pattern logic:
#     # If any aircraft is in a pattern, add it to active aircraft for displaying
#     # Once non-T1/T6/T38 aircraft depart the pattern, delete from active aircraft
 
    
#     patternDict = {}
#     for runway in Runway.objects.all():
#         patternPolygon = getKMLplacemark("./AutoRecorder" + runway.kmlPatternFile.url, runway.patternName)
#         patternDict[runway.patternName] = (patternPolygon, runway.patternAltitudeCeiling, runway.airfield.fieldElevation, runway.patternName)        

#     soloCallsignList = []
#     for callsign in Callsign.objects.filter(type='solo'):
#         soloCallsignList.append(callsign.callsign)

#     i = 0
#     while True:
#         logger.info("Requesting ADSB Data...")

#         newData = {
#             "ac": [] #add/remove aircraft to list here
#         } # dictionary...
#         with mutex:
#             newData = copy.deepcopy(jsondata)

#         # logfile = open(r"./AutoRecorder/testFiles/ADSBsnapshot" + str(i) + ".json", "w")
#         # logfile.write(json.dumps(jsondata))
#         # logfile.close
#         # i+=1

#         #print(jsondata)

#         updatedAircraftList = []
#         updatedAircraftObjects = [] 

#         activeAircraftObjects = ActiveAircraft.objects.all()
#         activeAircraftDict = {ActiveAircraft.tailNumber: ActiveAircraft for ActiveAircraft in activeAircraftObjects}

#         aircraftTypes = AircraftType.objects.all()
#         aircraftTypeDict = {AircraftType.aircraftType: AircraftType for AircraftType in aircraftTypes}

#         activeFormationX2 = list(activeAircraftObjects.filter(formationX2=True))
#         activeFormationX4 = list(activeAircraftObjects.filter(formationX4=True))

#         # logger.info(newData)
#         for aircraft in newData['ac']: #ac is aircraft in the database 
#             try:
#                 position = getPosition(aircraft)
#                 if str(aircraft["t"]) in aircraftTypeDict or inPattern(position, patternDict):
#                     logger.debug(aircraft['r'] + " is about to be updated or created...")

#                     try:
#                         Acft = activeAircraftDict[aircraft["r"][:-3] + "--" + aircraft["r"][-3:]]
#                     except KeyError as e:
#                         Acft = ActiveAircraft.objects.create(tailNumber=aircraft["r"][:-3] + "--" + aircraft["r"][-3:])
#                         logger.info('KeyError in aircraft ' + str(e) + "; however, this is ok. We just need to create a new aircraft")

                    
#                     try:
#                         Acft.aircraftType = aircraftTypeDict[aircraft["t"]]
#                     except KeyError as e:
#                         newType = AircraftType.objects.create(aircraftType=aircraft["t"])
#                         aircraftTypeDict[aircraft["t"]] = newType
#                         Acft.aircraftType = newType
#                         logger.info('KeyError in aircraft ' + str(e) + "; however, this is ok. We just need to create a new aircraft TYPE")


#                     Acft.callSign=aircraft["flight"]

#                     for callsign in soloCallsignList:
#                         if fuzz.ratio(Acft.callSign, callsign) >= 80:
#                             Acft.solo = True
#                     #formation=aircraft[""],                need form callsign db?
#                     # Acft.emergency=False if aircraft["emergency"] == "none" else True
#                     Acft.alt_baro=aircraft['alt_baro']
#                     Acft.groundSpeed=aircraft['gs']
#                     Acft.latitude=aircraft['lat']
#                     Acft.longitude=aircraft['lon']
#                     Acft.track=aircraft['track']
#                     Acft.squawk=aircraft['squawk']
#                     Acft.emergency = True if Acft.squawk == "7700" or Acft.squawk == "7600" or Acft.squawk == "7500" else False
#                     Acft.seen=aircraft['seen']
#                     Acft.rssi=aircraft['rssi']
#                     if Acft.alt_baro == "ground":
#                         position = geometry.Point(Acft.latitude, Acft.longitude, 0)
#                     else:
#                         position = geometry.Point(Acft.latitude, Acft.longitude, int(Acft.alt_baro))
#                     if inPattern(position, patternDict) and Acft.groundSpeed > Acft.aircraftType.fullStopThresholdSpeed and Acft.alt_baro != "ground" and Acft.state != "in pattern": 
#                         Acft.lastState = Acft.state
#                         Acft.state="in pattern"
#                         Acft.substate=setSubstate(position, Acft.state, patternDict)
#                         if Acft.lastState == "taxiing" or (Acft.lastState == None and int(Acft.alt_baro) < int(patternDict[Acft.substate][2] + 200)): # field elevation is the [2]nd element in each tuple within patternDict - this hard-codes a 200 ft threshold to deal with low-altitude adsb signal loss
#                             Acft.takeoffTime = timezone.now()
#                             try:
#                                 nextTOData = NextTakeoffData.objects.get(runway__patternName = Acft.substate)
#                                 Acft.solo = nextTOData.solo
#                                 Acft.formationX2 = nextTOData.formationX2
#                                 Acft.formationX4 = nextTOData.formationX4
#                                 resetNextTakeoffData(nextTOData)
#                                 logger.info("Next T/O Data applied!")
#                             except:
#                                 logger.error("Error processing next T/O data for acft with substate: " + Acft.substate)
                        
#                     elif inPattern(position, patternDict) and Acft.groundSpeed < Acft.aircraftType.fullStopThresholdSpeed and Acft.state != "taxiing" and (Acft.alt_baro == "ground" and int(Acft.alt_baro) < int(patternDict[Acft.substate][2] + 150)):
#                         Acft.lastState = Acft.state
#                         Acft.state="taxiing"
#                         Acft.substate=setSubstate(position, Acft.state, patternDict)
#                         if Acft.lastState == "in pattern":
#                             Acft.landTime = timezone.now()
#                     elif inPattern(position, patternDict) == False and Acft.state != "off station":
#                         Acft.lastState = Acft.state
#                         Acft.state="off station"
#                         Acft.substate=setSubstate(position, Acft.state, patternDict) 
#                     Acft.timestamp=timezone.now()
                    
#                    #form logic 
                    
#                 #2ship to 1ship logic 
#                 # Check if this aircraft is splitting from a 2 ship nearby
#                     closestFormation = None
#                     closestFormationDistance = None

#                     for formAcft in activeFormationX2:

#                         formAcftPosition = geometry.Point(0,0,0)
#                         if formAcft.alt_baro == "ground":
#                             formAcftPosition = geometry.Point(formAcft.latitude, formAcft.longitude, 0)
#                         else:
#                             formAcftPosition = geometry.Point(formAcft.latitude, formAcft.longitude, int(formAcft.alt_baro))

#                         if Acft.callSign == '':
#                             break
#                         if formAcft.callSign == '':
#                             continue
#                         if  Acft.callSign[:-1] == formAcft.callSign[:-1] and Acft.formationX2 is False:
#                             if int(Acft.callSign[-1:]) >=  int(formAcft.callSign[-1:]) - 1 or int(Acft.callSign[-1:]) <=  int(formAcft.callSign[-1:]) + 1:
#                                 distance = position.distance(formAcftPosition) * 69 #approx lat/lon -> miles conversion factor for CONUS
#                                 if (distance <= Acft.aircraftType.formationDistThreshold) and Acft.groundSpeed > Acft.aircraftType.fullStopThresholdSpeed and formAcft.groundSpeed > formAcft.aircraftType.fullStopThresholdSpeed:
#                                     if (Acft.lastState is None and Acft.takeoffTime is None) or (Acft.lastState is not None and Acft.formTimestamp is not None and formAcft.formTimestamp is not None) and (Acft.lastState == "lost signal" and abs(Acft.formTimestamp - formAcft.formTimestamp) <= timedelta(seconds=Acft.aircraftType.formationLostSignalTimeThreshold)):
#                                         if closestFormation is None or distance < closestFormationDistance:
#                                             closestFormation = formAcft
#                                             closestFormationDistance = distance

#                     if closestFormation is not None:
#                         #     if form.tailNumber == closestFormation.tailNumber:
#                         activeFormationX2.remove(closestFormation)
#                         closestFormation.formationX2 = False
#                         closestFormation.formTimestamp = timezone.now()
#                         Acft.formTimestamp = timezone.now()
#                         closestFormation.save()
                        
#                     #4 -> 2-ship logic

#                     closestFormation = None
#                     closestFormationDistance = None

#                     for formAcft in activeFormationX4:

#                         formAcftPosition = geometry.Point(0,0,0)
#                         if formAcft.alt_baro == "ground":
#                             formAcftPosition = geometry.Point(formAcft.latitude, formAcft.longitude, 0)
#                         else:
#                             formAcftPosition = geometry.Point(formAcft.latitude, formAcft.longitude, int(formAcft.alt_baro))

#                         if Acft.callSign == '':
#                             break
#                         if formAcft.callSign == '':
#                             continue
#                         if  Acft.callSign[:-1] == formAcft.callSign[:-1] and Acft.formationX4 is False:
#                             if int(Acft.callSign[-1:]) >=  int(formAcft.callSign[-1:]) - 3 or int(Acft.callSign[-1:]) <=  int(formAcft.callSign[-1:]) + 3:
#                                 distance = position.distance(formAcftPosition) * 69
#                                 if (distance <= Acft.aircraftType.formationDistThreshold) and Acft.groundSpeed > Acft.aircraftType.fullStopThresholdSpeed and formAcft.groundSpeed > formAcft.aircraftType.fullStopThresholdSpeed:
#                                     if (Acft.lastState is None and Acft.takeoffTime is None) or (Acft.lastState is not None and Acft.formTimestamp is not None and formAcft.formTimestamp is not None) and (Acft.lastState == "lost signal" and abs(Acft.formTimestamp - formAcft.formTimestamp) <= timedelta(seconds=Acft.aircraftType.formationLostSignalTimeThreshold)):
#                                         if closestFormation is None or distance < closestFormationDistance:
#                                             closestFormation = formAcft
#                                             closestFormationDistance = distance

#                     if closestFormation is not None:
#                         #     if form.tailNumber == closestFormation.tailNumber:
#                         activeFormationX2.remove(closestFormation)
#                         closestFormation.formationX2 = False
#                         closestFormation.formTimestamp = timezone.now()
#                         Acft.formTimestamp = timezone.now()
#                         closestFormation.save()

#                     Acft.save()
#                     logger.debug("Success!, Acft is" + Acft.tailNumber) 
#                     updatedAircraftList.append(Acft.tailNumber)     
#                     updatedAircraftObjects.append(Acft)

#             except KeyError as e:
#                 logger.error('KeyError in aircraft ' + str(e) + str(aircraft) + "; however, this is probably okay...")

#         aircraftNotUpdated = ActiveAircraft.objects.exclude(tailNumber__in=updatedAircraftList) # getAircraftNotUpdated(updatedAircraftList)
#         # logger.info('aircraft not updated: ' + str(aircraftNotUpdated))

# # TODO NEED TO THOROUGHLY TEST THE LOGIC ABOVE AND BELOW THIS LINE. STATE TRANSITIONS ARE CRITICAL TO GET RIGHT. 

#         if aircraftNotUpdated is not None:
#             for Acft in aircraftNotUpdated:
#                 # if Acft.timestamp or Acft.landTime or Acft.state or Acft.lastState is None:
#                 #     continue

#                     # Formation logic:
#                     # Departure 
#                     # Flying Around
#                     # Recovery
#                     # Four ships
#                     # Robust splits and rejoins


#                 position1 = geometry.Point(0, 0) 
#                 position2 = geometry.Point(0, 0)

#                 for freshAcft in updatedAircraftObjects:        #start form logic 
#                     # 1ship to 2ship logic )

#                     if freshAcft.callSign is not None and Acft.callSign is not None and freshAcft.callSign[:-1] == Acft.callSign[:-1]  and not freshAcft.formationX2 and not Acft.formationX2: 
#                         position1 = geometry.Point(Acft.latitude, Acft.longitude) if Acft.latitude is not None else geometry.Point(0, 0)    #find position of 1st jet
#                         position2 = geometry.Point(freshAcft.latitude, freshAcft.longitude) if freshAcft.latitude is not None else geometry.Point(0, 0)  #find position of 2nd jet 
                        
#                         if (position2.distance(position1) * 69 <= Acft.aircraftType.formationDistThreshold) and Acft.groundSpeed > Acft.aircraftType.fullStopThresholdSpeed and freshAcft.groundSpeed > freshAcft.aircraftType.fullStopThresholdSpeed:           # :)  degrees of lat & long to miles
#                             if abs(Acft.timestamp - timezone.now()) <= timedelta(seconds=Acft.aircraftType.formationLostSignalTimeThreshold):
#                                 if int(Acft.callSign[-1:]) >=  int(freshAcft.callSign[-1:]) - 1 or int(Acft.callSign[-1:]) <=  int(freshAcft.callSign[-1:]) + 1:
#                                     freshAcft.formationX2 = True
#                                     freshAcft.formTimestamp = timezone.now()
#                                     Acft.formTimestamp = timezone.now()
#                                     freshAcft.save()
#                                     Acft.save()

#                     # 2 -> 4-ship logic

#                     elif freshAcft.callSign is not None and Acft.callSign is not None and freshAcft.callSign[:-1] == Acft.callSign[:-1]  and freshAcft.formationX2 and Acft.formationX2: 
#                         position1 = geometry.Point(Acft.latitude, Acft.longitude) if Acft.latitude is not None else geometry.Point(0, 0)    #find position of 1st jet
#                         position2 = geometry.Point(freshAcft.latitude, freshAcft.longitude) if freshAcft.latitude is not None else geometry.Point(0, 0)  #find position of 2nd jet 
                        
#                         if (position2.distance(position1) * 69 <= Acft.aircraftType.formationDistThreshold) and Acft.groundSpeed > Acft.aircraftType.fullStopThresholdSpeed and freshAcft.groundSpeed > freshAcft.aircraftType.fullStopThresholdSpeed:           # :)  degrees of lat & long to miles
#                             if abs(Acft.timestamp - timezone.now()) <= timedelta(seconds=Acft.aircraftType.formationLostSignalTimeThreshold):
#                                 if int(Acft.callSign[-1:]) >=  int(freshAcft.callSign[-1:]) - 3 or int(Acft.callSign[-1:]) <=  int(freshAcft.callSign[-1:]) + 3:
#                                     freshAcft.formationX4 = True
#                                     freshAcft.formTimestamp = timezone.now()
#                                     Acft.formTimestamp = timezone.now()
#                                     freshAcft.save()
#                                     Acft.save()

#                 position = geometry.Point(Acft.latitude, Acft.longitude) if Acft.latitude is not None else geometry.Point(0, 0)
#                 if Acft.timestamp is not None and (timezone.now() - Acft.timestamp).total_seconds() > LOST_SIGNAL_TIME_THRESHOLD_SECONDS: # 5 sec
#                     if Acft.landTime == None and Acft.state != "lost signal":
#                         Acft.lastState = Acft.state
#                         Acft.state = "lost signal"
#                         Acft.substate=Acft.substate=setSubstate(position, Acft.state, patternDict)
#                         Acft.save()
#                         logger.info("lost signal")
#                     elif Acft.landTime != None and Acft.state != "completed sortie":
#                         Acft.lastState = Acft.state
#                         Acft.state = "completed sortie"
#                         Acft.substate=Acft.substate=setSubstate(position, Acft.state, patternDict)
#                         Acft.save()
#                         logger.info("completed sortie")
#                 if Acft.timestamp is not None and (timezone.now() - Acft.timestamp).total_seconds() > LOST_SIGNAL_TO_COMPLETED_SORTIE_TIME_THRESHOLD_HOURS*3600: #4 hrs
#                     Acft.lastState = Acft.state
#                     Acft.state = "completed sortie"
#                     Acft.substate=Acft.substate=setSubstate(position, Acft.state, patternDict)
#                     Acft.save()
#                     logger.info("completed sortie")

#         killSignal = True
#         threads_list = threading.enumerate()
        
#         for thread in threads_list:
#             if thread.name is parentThreadName and thread.is_alive() is True:
#                 killSignal = False
        
#         if killSignal is False:
#             logger.info("ADSB Thread sleeping...")
#             time.sleep(.2)
#             logger.info("ADSB Thread waking up...")

#             continue
#         else:
#             logger.debug("Stopping ADSB Thread")
#             os.environ['ENABLE_ADSB'] = 'True'
#             return



# def commsTestThread(parentThreadName):
#     import websocket
#     import json
#     import time
#     dummyWebSocket = websocket.WebSocket()

#     with open(r"./AutoRecorder/testFiles/Stratux/ADSBsnapshots.json") as logfile:
#         data = json.load(logfile)

#         for message in data["testData"]:
#             on_message(dummyWebSocket, json.dumps(message))

#             killSignal = True
#             threads_list = threading.enumerate()
            
#             for thread in threads_list:
#                 if thread.name is parentThreadName and thread.is_alive() is True:
#                     killSignal = False
            
#             if killSignal is False:
#                 # logger.info("Comms Test Thread sleeping...")
#                 time.sleep(0.02)
#                 # logger.info("Comms Test Thread waking up...")
 
#                 continue
#             else:
#                 logger.debug("Stopping Comms Test Thread")
#                 os.environ['ENABLE_ADSB'] = 'True'
#                 return



# def stratuxCommsThread(address):
#     import websocket
#     wsapp = websocket.WebSocketApp(address, on_message=on_message,)
#     logger.info("Connecting to Stratux now...")
#     wsapp.run_forever()

   


 
# def on_message(ws, message):
#     # Manipulate message from Stratux format to ADSB Exchange format. See stratux.json in testFiles for comments
#     dictMessage = json.loads(message)

#     # logfile = open(r"./AutoRecorder/testFiles/Stratux/ADSBsnapshots" + ".json", "a+")
#     # logfile.write(json.dumps(dictMessage))
#     # logfile.close
    
#     # Do nothing with signals that don't have a valid position
#     if dictMessage['Lat'] == 0 or dictMessage["Lng"] == 0:
#         deleteOldAircraft()
#         # logger.info("Aircraft " + dictMessage["Tail"] + "not saved since it had a null position")
#         return
#     reformattedMessage = Stratux_to_ADSBExchangeFormat(message)
#     with mutex:
#         aggregate(reformattedMessage)
#     # with mutex:
#         deleteOldAircraft()
#         # print(jsondata)

# # create an aggregate .json file with all traffic every second infinitely
# def aggregate(reformattedMessage):
#     reformattedMessage = json.loads(reformattedMessage)
#     # print("yeehaw... This should work this time...")
#     i = 0
#     for acft in jsondata["ac"]:
#         # print("entering loop")
#         # print("acft is" + str(acft))
#         # print("jsondata is: " + str(jsondata))
#         # print("reformattedMessage is: " + str(reformattedMessage))
#         # print("acft registration is: " + acft["r"])
#         # print("reformatted registration is: " + reformattedMessage["r"])
#         if acft["r"] == reformattedMessage["r"]:
#             # print("!!!!!!!!!!!!!!!!!!!!")
#             jsondata['ac'][i] = reformattedMessage
#             # print(jsondata)
#             return
#         i+=1
#     # if acft does not currently have an entry in jsondata, then add it
#     jsondata["ac"].append(reformattedMessage)
#     # print(jsondata)
#     return

# def deleteOldAircraft():
#     # print("this function will delete all acft older than 1min from jsondata")
    
#     for acft in jsondata["ac"]:
#         # print("made it")
#         if acft['seen'] >= 59.0:
#             print("ABOUT TO REMOVE " + acft['flight'] + "from jsondata.")
#             jsondata["ac"].remove(acft)
#             print("REMOVED " + acft['flight'] + "from jsondata.")

#         # timestamp = parser.parse(acft["Timestamp"])
#         # if (timezone.now() - timestamp).seconds > 60:
#         #     jsondata["ac"].remove(acft)
        

# def Stratux_to_ADSBExchangeFormat(inputMessage):

#     JSONmessage = json.loads(inputMessage) 

#     hexKey = hex(JSONmessage['Icao_addr'])[2:].upper()

#     acft = USAircraft[hexKey] # successfully got this: {'r': '04-3756', 't': 'TEX2', 'f': '10', 'd': 'Raytheon T-6A Texan II'}

#     #grab r & t from    USAircraft[hexKey] 
#     JSONmessage['r'] = acft["r"]
#     JSONmessage['t'] = acft["t"]
#     JSONmessage['d'] = acft['d']
#     JSONmessage['hex'] = hex(JSONmessage.pop('Icao_addr'))[2:]   # replace 
#     JSONmessage['flight'] = JSONmessage.pop('Tail')   # replace "Tail" key with "flight" key 
#     JSONmessage['dbFlags'] = JSONmessage['TargetType']
#     JSONmessage['alt_baro'] =  "ground" if JSONmessage.pop('OnGround') is True else str(JSONmessage.pop('Alt'))
#     JSONmessage['rssi'] = JSONmessage.pop('SignalLevel')
#     JSONmessage['squawk'] = JSONmessage.pop('Squawk')
#     JSONmessage['lat'] = JSONmessage.pop('Lat')
#     JSONmessage['lon'] = JSONmessage.pop('Lng')
#     JSONmessage['baro_rate'] = JSONmessage.pop('Vvel')
#     JSONmessage['nic'] = JSONmessage.pop('NIC')
#     JSONmessage['nac_p'] = JSONmessage.pop('NACp')
#     JSONmessage['track'] = JSONmessage.pop('Track')
#     JSONmessage['gs'] = JSONmessage.pop('Speed')
#     JSONmessage['seen'] = JSONmessage.pop('Age')

#     # print(JSONmessage)
#     outputJSON = json.dumps(JSONmessage)
#     return outputJSON


# def adsbExchangeCommsThread(parentThreadName, lat, lon, radius):
#     import http.client
#     import json
#     import time

#     conn = http.client.HTTPSConnection("adsbexchange-com1.p.rapidapi.com")

#     headers = {
#         'X-RapidAPI-Key': "e7a36b9597msh0954cc7e057677dp160f6fjsn5e333eceedc4",
#         'X-RapidAPI-Host': "adsbexchange-com1.p.rapidapi.com"
#         }

#     while True:

#         request = "/v2/lat/" + str(lat) + "/lon/" + str(lon) + "/dist/" + str(radius) + "/"
#         conn.request("GET", request, headers=headers)
#         print(request)
        
#         res = conn.getresponse()
#         data = res.read()

#         with mutex:
#             jsondata["ac"] = json.loads(data["ac"])
#             # print(jsondata)

#         killSignal = True
#         threads_list = threading.enumerate()
        
#         for thread in threads_list:
#             if thread.name is parentThreadName and thread.is_alive() is True:
#                 killSignal = False
        
#         if killSignal is False:
#             logger.info("ADSB Exchange Comms Thread sleeping...")
#             time.sleep(1)
#             logger.info("ADSB Exchange Comms Thread waking up...")

#             continue
#         else:
#             logger.debug("Stopping ADSB Exchange Comms Thread")
#             os.environ['ENABLE_ADSB'] = 'True'
#             return



# def inPattern(position, patternDict):
#     alt = position.z
#     position2d = geometry.Point(position.x, position.y)  
#     for pattern in patternDict:
#         if position2d.within(patternDict[pattern][0]) and alt < patternDict[pattern][1]: #[0] is the geometric shape, [1] is the altitudeCeiling
#             return True
#         else:
#             continue
#     return False


# def getKMLplacemark(file, placemarkName):
#     k = kml.KML()
#     with open(file, 'rt', encoding='utf-8') as myfile:
#         doc = myfile.read().encode('utf-8')
#     k.from_string(doc)
#     placemarks = []
#     parse_placemarks(placemarks, list(k.features()))
#     # print(k.to_string(prettyprint=True))
#     for placemark in placemarks:
#         if placemark.name == placemarkName:
#             return swapLatLong(placemark.geometry)


# def swapLatLong(polygon):
#     coordList = list(polygon.exterior.coords)
#     swappedCoordList = []
#     for point in coordList:
#         newPoint = point[1], point[0]
#         swappedCoordList.append(newPoint)
#     polygon = geometry.Polygon(swappedCoordList)
#     return polygon


# def parse_placemarks(target, document):
#     for feature in document:
#         if isinstance(feature, kml.Placemark):  
#            placemark = feature
#            target.append(placemark)
#     for feature in document:
#         if isinstance(feature, kml.Folder):
#             parse_placemarks(target, list(feature.features()))
#         if isinstance(feature, kml.Document):
#            parse_placemarks(target, list(feature.features()))


# def getAircraftNotUpdated(updatedAircraftList):
#     from AutoRecorder.models import ActiveAircraft
#     return ActiveAircraft.objects.exclude(tailNumber__in=updatedAircraftList)


# def getPosition(aircraft):
#     if aircraft["alt_baro"] == "ground":
#         position = geometry.Point(aircraft["lat"], aircraft["lon"], 1300)
#     else:
#         position = geometry.Point(aircraft["lat"], aircraft["lon"], int(aircraft["alt_baro"]))
#     return position


# def setSubstate(position, state, patternDict):

#     if state=="in pattern" or state=="taxiing" or state=="completed sortie":

#         for pattern in patternDict:
#             if position.within(patternDict[pattern][0]):
#                 return patternDict[pattern][3]
#     return "null"


# def resetNextTakeoffData(nextTOData):
#     nextTOData.solo = False
#     nextTOData.formationX2 = False
#     nextTOData.formationX4 = False 
#     nextTOData.save()
        
# global killSignals
# killSignals = {}
# # commsManagment
# def commsManagment(parentThreadName):
#     """Loop to ADSB sources and make sure status is not inactive
#     Every second Monitor and make sure"""

#     from AutoRecorder.models import ADSBSource

#     while True:

#         # Get a list of all active ADSB sources
#         adsbSources=ADSBSource.objects.all() 

#         # List of all running threads
#         threads_list = threading.enumerate()

#         for source in adsbSources:
#             # Kill any threads if the source is declared inactive
#             if source.threadSwitch is False:
#                 for thread in threads_list:
                    
#                     # Check if the thread name matches the source
#                     if thread.name == "adsbSourceThread" + str(source.id):
                        
#                         # Set the killSignal to false
#                         killSignals[thread.name] = False                     
                
#             else:
#                 # Convience variable to not be adding the strings together
#                 threadName = "adsbSourceThread" + str(source.id)

#                 # Check if the thread with the source ID exists
#                 continueSignal = None 
#                 for thread in threads_list:
#                     if thread.name == threadName: 
#                         continueSignal = True               

#                 # If the thread doesn't exist create and start a new thread
                
#                 if continueSignal is True:
#                     continue
#                 else:
#                     CommsThread = threading.Thread(target=adsbSource, args=(parentThreadName, source,), name="adsbSourceThread" + str(source.id))
#                     # Set the killSignal to true
#                     killSignals[threadName] = True
#                     CommsThread.start()
#                     print("Starting thread..." + str(CommsThread))
#                     print("threads_list is: " + str(threads_list))

#                     print(killSignals)


#         killSignal = True
#         threads_list = threading.enumerate()
        
#         for thread in threads_list:
#             if thread.name is parentThreadName and thread.is_alive() is True:
#                 killSignal = False
        
#         if killSignal is False:
#             # logger.info("ADSB Exchange Comms Thread sleeping...")
#             time.sleep(1)
#             # logger.info("ADSB Exchange Comms Thread waking up...")

#             continue
#         else:
#             # logger.debug("Stopping ADSB Exchange Comms Thread")
#             os.environ['ENABLE_ADSB'] = 'True'
#             return


# def adsbSource(parentThreadName, source): #takes new source of ADSB data that was created and put it info on a new thread, make connection, process data, get permission to edit mutex json and insert data.
   
#     threadName = "adsbSourceThread" + str(source.id)

#     while killSignals[threadName] == True:
       
#         #-> call stratuxCommThread
#         if source.sourceType == 'Local' :
#             logger.info("Starting stratuxComms...")
#             stratuxCommsThread(source.address)
#         elif source.sourceType == 'Historical':
#             commsTestThread(parentThreadName)
#         else :
#             adsbExchangeCommsThread(parentThreadName,source.lat,source.lon, source.radius)#partent thread name,lat,long,source radius

#         killSignal = True
#         threads_list = threading.enumerate()
        
#         for thread in threads_list:
#             if thread.name is parentThreadName and thread.is_alive() is True:
#                 killSignal = False
        
#         if killSignal is False:
#             # logger.info("ADSB Exchange Comms Thread sleeping...")
#             time.sleep(1)
#             # logger.info("ADSB Exchange Comms Thread waking up...")

#             continue
#         else:
#             # logger.debug("Stopping ADSB Exchange Comms Thread")
#             os.environ['ENABLE_ADSB'] = 'True'
#             return

#     return

# #[<_MainThread(MainThread, started 310004)>, <Thread(MessageThread, started 279932)>, <Thread(CommsTestThread, started 307460)>, <Thread(ADSBProcessingThread, started 301936)>]