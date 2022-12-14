import websocket
import json
import threading
from time import sleep
websocket.enableTrace(True)


"""
Stratux -> ADSB Exchange Data Format Conversion

See comments in stratux.json for json data conversion needs.

To replicate ADSB Exchange's data stream parameters, 
we should aggregate responses every second, convert to their
data format, then ship over to apps.py like normal...

This will also allow us to integrate ADSB Exchange's API 
directly (after scrubbing their API response for duplicate
entries - giving precedence to the newest data)

"""




def on_message(ws, message):
    # Manipulate message from Stratux format to ADSB Exchange format. See stratux.json in testFiles for comments
    logfile = open(r"./testFiles/Stratux/stratuxAggregate.json","a+")
    stratuxAggregate = json.load(logfile)
    jsondata = json.loads(message)

    # Mary function call here on the jsondata variable
    # Stratux_to_ADSBExchangeFormat(jsondata)

    for acft in jsondata:
        acft.update({"r": acft["Icao_addr"]})

    ADSBExchangeFormat = {'ac': jsondata, 'ready': False}

    for newAcft in ADSBExchangeFormat['ac']:
        for oldAcft in stratuxAggregate['ac']:
            if oldAcft['r'] == newAcft['r']:
                oldAcft = newAcft
                break
        stratuxAggregate['ac'].append(newAcft)
            

    logfile.write(json.dumps(stratuxAggregate))
    logfile.close
    print(stratuxAggregate)

# create an aggregate .json file with all traffic every second infinitely
def aggregate(parentThreadName):
    killSignal = False
    while killSignal is False:
        logfile = open(r"./testFiles/Stratux/stratuxAggregate.json","w+")
        stratuxAggregate = json.load(logfile)
        stratuxAggregate["ready"] = True
        logfile.write(json.dumps(stratuxAggregate))
        logfile.close

        killSignal = True
        threads_list = threading.enumerate()
    
        for thread in threads_list:
            if thread.name is parentThreadName and thread.is_alive() is True:
                killSignal = False
        
        if killSignal is False:
            sleep(1)
            continue
        else:
            return


aggregateThread = threading.Thread(target=aggregate, args=(threading.current_thread().name,), name='aggregateThread')
aggregateThread.start()

wsapp = websocket.WebSocketApp("ws://192.168.10.1/traffic", on_message=on_message)
wsapp.run_forever()

def Stratux_to_ADSBExchangeFormat(inputJSON):
    inputJSON = """ 
    {
    "Icao_addr": 11408330, // dec -> hex, then use hex as key for dict lookup to get 'r' and 't' tags
    "Reg": "",
    "Tail": "FURY04", //maps to 'flight'
    "Emitter_category": 1,
    "SurfaceVehicleType": 0,
    "OnGround": false, //combine with Alt to get 'alt_baro' 
    "Addr_type": 0, //
    "TargetType": 1, //'dbFlags'
    "SignalLevel": -20.357875270301804, //'rssi'
    "SignalLevelHist": [
        -24.55188088242224,
        -22.256290401500834,
        -20.497812333581365,
        -20.357875270301804,
        -20.743270060787594,
        -24.96754228534887,
        -24.591701858889202,
        -26.332036167132703
    ],
    "Squawk": 4301, //'squawk'
    "Position_valid": true,
    "Lat": 36.353348, //'lat'
    "Lng": -97.89047, //'lon'
    "Alt": 2575, //combine with OnGround above to get 'alt_baro'
    "GnssDiffFromBaroAlt": -350, //'baro_rate'
    "AltIsGNSS": false,
    "NIC": 10, //'nic'
    "NACp": 10, //'nac_p'
    "Track": 360, //'track'
    "TurnRate": 0, 
    "Speed": 138, //'gs'
    "Speed_valid": true,
    "Vvel": -512,
    "Timestamp": "2022-04-04T17:27:12.721Z",
    "PriorityStatus": 0,
    "Age": 0.35, //'seen'
    "AgeLastAlt": 0.35,
    "Last_seen": "0001-01-01T02:39:51.93Z",
    "Last_alt": "0001-01-01T02:39:51.93Z",
    "Last_GnssDiff": "0001-01-01T02:39:51.93Z",
    "Last_GnssDiffAlt": 2575,
    "Last_speed": "0001-01-01T02:39:51.93Z",
    "Last_source": 1,
    "ExtrapolatedPosition": false,
    "Last_extrapolation": "0001-01-01T02:39:07.85Z",
    "AgeExtrapolation": 43.17,
    "Lat_fix": 36.33551,
    "Lng_fix": -97.91074,
    "Alt_fix": 1775,
    "BearingDist_valid": false,
    "Bearing": 0,
    "Distance": 0,
    "DistanceEstimated": 26273.559990842597,
    "DistanceEstimatedLastTs": "2022-04-04T17:27:12.721Z",
    "ReceivedMsgs": 1013,
    "IsStratux": false
}
    """
    print("do things with json and dictionaries such that outputJSON contains the input data in ADSB Exchange format") 
    outputJSON = inputJSON
    return outputJSON