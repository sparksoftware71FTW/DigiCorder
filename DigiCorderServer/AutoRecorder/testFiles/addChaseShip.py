from copy import deepcopy
import json # json.loads(source) sends a source json file to a python dict and json.dumps(source)
            # sends a source python dict to a string with proper json formatting... 
            # We need to loop through the loaded aircraft objects in each file similar to how we do it in 
            # apps.py, look for DRAGN04, copy that data, modify it to be DRAGN05, change its position to be
            # <2mi from DRAGN04, and append DRAGN05 to the file.
            # 

i = 200
while i <= 277:
    with open(r"./AutoRecorder/testFiles/ADSBsnapshot" + str(i) + ".json", "r+") as logfile:
        jsondata = json.load(logfile)

        print(r"./AutoRecorder/testFiles/ADSBsnapshot" + str(i) + ".json")

        for aircraft in jsondata['ac']:
            #Get callsign, but catch dict KeyErrors if the aircraft object does not have a 'flight' key/callsign element
            try:
                callsign = aircraft["flight"]
                print(callsign)
                if callsign.__contains__('DRAGN04'):
                    dragon05 = deepcopy(aircraft)     #dragon05 is the ghost plane for testing 
                    dragon05["r"] = "01-3611"
                    print("dragon05 is: " + str(dragon05))
                    print("aircraft is: " + str(aircraft))
                    dragon05["flight"] = 'DRAGN05'
                    dragon05["lat"] = aircraft["lat"] - 0.01875   # 1 mil = 0.05625 decimal degree  = approx 3.2mi => 0.05625/3 = 1mi. approx         
                    jsondata['ac'].append(dragon05)
                    logfile.seek(0)
                    json.dump(jsondata, logfile, indent=4)

            #Continue to next aircraft if no callsign element
            except KeyError:
                print("No callsign")
                continue
    i+=1
        
            


