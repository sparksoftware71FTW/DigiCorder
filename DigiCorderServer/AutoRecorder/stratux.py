import websocket
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
    print(message)

wsapp = websocket.WebSocketApp("ws://192.168.10.1/traffic", on_message=on_message)
wsapp.run_forever(reconnect=3)

# create an aggregate .json file with all traffic every second infinitely
def aggregate():
    print('yeehaw')
