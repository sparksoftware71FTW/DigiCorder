import json # json.loads(source) sends a source json file to a python dict and json.dumps(source)
            # sends a source python dict to a string with proper json formatting... 
            # We need to loop through the loaded aircraft objects in each file similar to how we do it in 
            # apps.py, look for DRAGN04, copy that data, modify it to be DRAGN05, change its position to be
            # <2mi from DRAGN04, and append DRAGN05 to the file.
            # 

i = 3
while True:
    logfile = open(r"./AutoRecorder/testFiles/ADSBsnapshot" + str(i) + ".json", "r")
    jsondata = json.loads(logfile.read())



