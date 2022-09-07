from codecs import latin_1_decode
from telnetlib import STATUS
from tkinter import CASCADE
from unicodedata import name
from django.db import models
# from django.db.models.signals import post_save
# from django.dispatch import receiver
from django.utils import timezone
# Create your models here.

class Message(models.Model):
    message = models.CharField('message', max_length=150, blank=True, null=True)

    def __str__(self):
        return "id " + str(self.id)

class Airfield(models.Model):
    FAAcode = models.CharField('FAA Code', max_length=4, primary_key=True)
    name = models.CharField('Name', max_length=40, blank=True, null=True)

    def __str__(self):
        return "FAAcode " + str(self.FAAcode)

class Callsigns(models.Model):
    callsign = models.CharField('Callsigns', max_length=20, primary_key=True)
    aircraftType = models.CharField('Aircraft Type', max_length=20, blank=True, null=True)
    typoe = models.CharField('Type', max_length=20, default="dual")
    homeField = models.ForeignKey(Airfield, on_delete=models.CASCADE)

class Tails(models.Model):
    tail = models.CharField('Tail', max_length=15, primary_key=True)
    airfield = models.ForeignKey(Airfield, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return "callsign " + str(self.callsign) 

class Runway(models.Model):
    name = models.CharField('Name', max_length=4, primary_key=True)
    primaryAircraftType = models.CharField('Primary Aircraft Type', max_length=20, blank=True, null=True)
    airfield = models.OneToOneField(Airfield, on_delete=models.CASCADE)

    def __str__(self):
        return "name " + str(self.name) 

class Pattern(models.Model):
    lat = models.DecimalField("lat", decimal_places=10, max_digits=13)
    lon = models.DecimalField("lon", decimal_places=10, max_digits=13)
    alt = models.DecimalField("altitude", decimal_places=2, max_digits=7)
    runway = models.OneToOneField(Runway, on_delete=models.CASCADE)

    def __str__(self):
        return "pattern point (lat,lon,alt): " + str(self.lat) + ", " + str(self.lon) + "," + str(self.alt)

class ActiveAircraft(models.Model):
    tailNumber = models.CharField('Tail', primary_key=True, max_length=15)
    aircraftType = models.CharField('Type', max_length=20, blank=True, null=True)
    callSign = models.CharField('Callsign', max_length=12, blank=True, null=True)
    takeoffTime = models.DateTimeField('Takeoff Time', blank=True, null=True)
    three55Code = models.CharField('355 Code', max_length=5, default='none')
    Comments = models.CharField('Comments', max_length=200, default='none')
    landTime = models.DateTimeField('Final Landing Time', blank=True, null=True)
    solo = models.BooleanField('Solo', default=False)
    formation = models.BooleanField('Formation', default=False)
    emergency = models.BooleanField('Emergency', default=False)
    natureOfEmergency = models.CharField('Nature of Emergency:', max_length=200, blank=True, null=True)
    groundSpeed = models.DecimalField('Ground Speed', default=0.000, decimal_places=3, max_digits=7)
    latitude = models.DecimalField('Lat', blank=True, null=True, decimal_places=7, max_digits=10)
    longitude = models.DecimalField('Lon', blank=True, null=True, decimal_places=7, max_digits=10)
    alt_baro = models.CharField('Altitude', max_length=12, blank=True, null=True,)
    alt_geom = models.CharField('Altitude-Geometric', max_length=12, blank=True, null=True)
    track = models.DecimalField('Track', blank=True, null=True, decimal_places=3, max_digits=6)
    squawk = models.CharField('Squawk', max_length=10, blank=True, null=True)
    seen = models.DecimalField('seen', blank=True, null=True, decimal_places=2, max_digits=6)
    rssi = models.DecimalField('rssi', blank=True, null=True, decimal_places=3, max_digits=6)
    state = models.CharField('State', max_length=20, blank=True, null=True)  # 'taxiiing', 'in home pattern', 'off station', 'lost signal', or 'completed sortie'
    lastState = models.CharField('State', max_length=20, blank=True, null=True)  # 'taxiiing', 'in home pattern', 'off station', 'lost signal', or 'completed sortie'
    homeField = models.ForeignKey(Airfield, on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField('Timestamp', blank=True, null=True)


    def __str__(self):
        return "Tail " + str(self.tailNumber)

class CompletedSortie(models.Model):
    aircraftType = models.CharField('Type', max_length=20, blank=True, null=True)
    tailNumber = models.IntegerField('Tail Number')
    callSign = models.CharField('Callsign', max_length=12, blank=True, null=True)
    takeoffTime = models.DateTimeField('Takeoff Time', blank=True, null=True)
    three55Code = models.CharField('355 Code', max_length=5, default='none')
    Comments = models.CharField('Comments', max_length=200, default='none')
    landTime = models.DateTimeField('Final Landing Time', blank=True, null=True)
    solo = models.BooleanField('Solo', default=False)
    formation = models.BooleanField('Formation', default=False)
    emergency = models.BooleanField('Emergency', default=False)
    natureOfEmergency = models.CharField('Nature of Emergency:', max_length=200, blank=True, null=True)
    groundSpeed = models.DecimalField('Ground Speed', default=0.000, decimal_places=3, max_digits=7)
    latitude = models.DecimalField('Lat', blank=True, null=True, decimal_places=7, max_digits=10)
    longitude = models.DecimalField('Lon', blank=True, null=True, decimal_places=7, max_digits=10)
    alt_baro = models.CharField('Altitude', max_length=12, blank=True, null=True,)
    alt_geom = models.CharField('Altitude-Geometric', max_length=12, blank=True, null=True)
    track = models.DecimalField('Track', blank=True, null=True, decimal_places=3, max_digits=6)
    squawk = models.CharField('Squawk', max_length=10, blank=True, null=True)
    seen = models.DecimalField('seen', blank=True, null=True, decimal_places=2, max_digits=6)
    rssi = models.DecimalField('rssi', blank=True, null=True, decimal_places=3, max_digits=6)
    state = models.CharField('State', max_length=20, blank=True, null=True)  # 'taxiiing', 'in home pattern', 'off station', 'lost signal', or 'completed sortie'
    lastState = models.CharField('State', max_length=20, blank=True, null=True)  # 'taxiiing', 'in home pattern', 'off station', 'lost signal', or 'completed sortie'
    homeField = models.ForeignKey(Airfield, on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField('Timestamp', blank=True, null=True)


    def __str__(self):
        return "id " + str(self.id)



