import django
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'DigiCorderServer.settings'
django.setup()
from AutoRecorder.models import Message
newMessage = Message.objects.create(message="which process will the signal pop in?")
#This will trigger signals in whatever process is running it...