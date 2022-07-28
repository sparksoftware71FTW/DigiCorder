from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
# Create your models here.

class Active_T6(models.Model):
    tailNumber = models.IntegerField('Tail', primary_key=True)
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

    def __str__(self):
        return self.callSign

class Completed_T6_Sortie(models.Model):
    tailNumber = models.IntegerField('Tail Number')
    callSign = models.CharField('Callsign', max_length=12)
    takeoffTime = models.DateTimeField('Takeoff Time')
    landTime = models.DateTimeField('Final Landing Time')
    three55 = models.CharField('355 Comments', max_length=100, default='none')
    solo = models.BooleanField('Solo', default=False)
    formation = models.BooleanField('Formation', default=False)
    crossCountry = models.BooleanField('X-Country', default=False)
    localFlight = models.BooleanField('LocalFlight', default=True)
    inEastsidePattern = models.BooleanField('Currently in Eastside Pattern', default=True)
    emergency = models.BooleanField('Emergency', default=False)
    natureOfEmergency = models.CharField('Nature of Emergency:', max_length=200)

    def __str__(self):
        return self.callSign