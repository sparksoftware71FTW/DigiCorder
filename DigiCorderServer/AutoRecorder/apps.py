import os
import threading
import asyncio
import time
import http.client
from django.apps import AppConfig
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async


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
        run_once = os.environ.get('RUN_ONCE') 
        if run_once is not None:
            return
        os.environ['RUN_ONCE'] = 'True'
        print("ready() thread is: " + threading.current_thread().name)
        t1 = threading.Thread(target=task1, args=(threading.current_thread().name,), name='t1')
        t1.start()
            
def task1(parentThreadName):
    from AutoRecorder.models import Active_T6
    print("Task 1 assigned to thread: {}".format(threading.current_thread().name))
    print("ID of process running task 1: {}".format(os.getpid()))
    
    while True:
        conn = http.client.HTTPSConnection("adsbexchange-com1.p.rapidapi.com")

        headers = {
            'X-RapidAPI-Key': "e7a36b9597msh0954cc7e057677dp160f6fjsn5e333eceedc4",
            'X-RapidAPI-Host': "adsbexchange-com1.p.rapidapi.com"
            }

        conn.request("GET", "/v2/lat/51.46888/lon/-0.45536/dist/50/", headers=headers)

        res = conn.getresponse()
        data = res.read()

        print(data.decode("utf-8"))

        killSignal = True
        threads_list = threading.enumerate()
        
        for thread in threads_list:
            print("thread.name is " + thread.name)
            print("thread.is_alive() returns: ", thread.is_alive())
            if thread.name is parentThreadName and thread.is_alive() is True:
                killSignal = False
        
        if killSignal is False:
            time.sleep(3)
            continue
        else:
            return