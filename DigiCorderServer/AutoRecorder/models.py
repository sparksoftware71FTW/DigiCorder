from codecs import latin_1_decode
from telnetlib import STATUS
from django.db import models
# from django.db.models.signals import post_save
# from django.dispatch import receiver
from django.utils import timezone
# Create your models here.

class Active_T6(models.Model):
    tailNumber = models.CharField('Tail', primary_key=True, max_length=15)
    callSign = models.CharField('Callsign', max_length=12, blank=True, null=True)
    takeoffTime = models.DateTimeField('Takeoff Time', blank=True, null=True)
    three55Code = models.CharField('355 Code', max_length=5, default='none')
    Comments = models.CharField('Comments', max_length=200, default='none')
    landTime = models.DateTimeField('Final Landing Time', blank=True, null=True)
    solo = models.BooleanField('Solo', default=False)
    formation = models.BooleanField('Formation', default=False)
    crossCountry = models.BooleanField('X-Country', default=False)
    localFlight = models.BooleanField('LocalFlight', default=True)
    inEastsidePattern = models.BooleanField('Eastside Pattern', default=True)
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
    state = models.CharField('State', max_length=20, blank=True, null=True)


    def __str__(self):
        return "Tail " + str(self.tailNumber)

class Completed_T6_Sortie(models.Model):
    tailNumber = models.IntegerField('Tail Number')
    callSign = models.CharField('Callsign', max_length=12, blank=True, null=True)
    takeoffTime = models.DateTimeField('Takeoff Time', blank=True, null=True)
    three55Code = models.CharField('355 Code', max_length=5, default='none')
    Comments = models.CharField('Comments', max_length=200, default='none')
    landTime = models.DateTimeField('Final Landing Time', blank=True, null=True)
    solo = models.BooleanField('Solo', default=False)
    formation = models.BooleanField('Formation', default=False)
    crossCountry = models.BooleanField('X-Country', default=False)
    localFlight = models.BooleanField('LocalFlight', default=True)
    inEastsidePattern = models.BooleanField('Eastside Pattern', default=True)
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
    state = models.CharField('State', max_length=20, blank=True, null=True)

    def __str__(self):
        return "Tail " + str(self.tailNumber)

class Message(models.Model):
    message = models.CharField('message', max_length=150, blank=True, null=True)