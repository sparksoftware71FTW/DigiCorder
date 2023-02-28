from email.policy import default
from unittest.util import _MAX_LENGTH
from django.db import models
import json
from django.contrib.auth.models import Group, User
from django.db.models import Q
from django.utils import timezone
from django.utils.timezone import timedelta
from django.core import serializers
from django.core.validators import RegexValidator

"""
models.py is the location in which we define our database models.

The classes currently defiened are Messages, Triggers, Airfield, 
AdditionalKML, GroupExtras, Tails, AircraftType, RunwayManager, Callsign, Runway, UserDisplayExtra, 
RsuCrew, ActiveAircraftManager, ActiveAircraft, CompletedSortie, NextTakeoffData, ADSBSource, and CommsControl

These models can be expaned upon depending on the needs of the project.

"""

alphanumeric = RegexValidator(r'^[0-9a-zA-Z _]*$', 'Only alphanumeric characters are allowed.')


class Message(models.Model):
    message = models.CharField('message', max_length=150, blank=True, null=True)

    def __str__(self):
        return "id " + str(self.id)

class Trigger(models.Model):
    sendAllMessages = models.BooleanField('Send Message', default=False)

class Airfield(models.Model):
    FAAcode = models.CharField('FAA Code', max_length=4, primary_key=True)
    name = models.CharField('Name', max_length=40, blank=True, null=True)
    userGroup = models.OneToOneField(Group, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name="User Group (note: this will automatically set itself to a group with an identical name to 'FAA Code')")
    lat = models.DecimalField('Latitude', blank=True, null=True, decimal_places=7, max_digits=10)
    lon = models.DecimalField('Longitude', blank=True, null=True, decimal_places=7, max_digits=10)
    fieldElevation = models.DecimalField('Field Elevation', decimal_places=3, max_digits=8, blank=True, null=True)


WEIGHTS = ((1, 'Low'), (3, 'Medium'), (5, 'High'))
COLORS = [('#00ffff', 'aqua'), ('#000000', 'black'), ('#0000ff', 'blue'), ('#ff00ff', 'fuchsia'), ('#008000', 'green'), ('#808080', 'gray'), ('#00ff00', 'lime'), ('#800000', 'maroon'), ('#000080', 'navy'), ('#808000', 'olive'), ('#800080', 'purple'), ('#ff0000', 'red'), ('#c0c0c0', 'silver'), ('#008080', 'teal'), ('#ffffff', 'white'), ('#ffff00', 'yellow')]

class AdditionalKML(models.Model):
    file = models.FileField(upload_to='kml')
    color = models.CharField(max_length=9, choices=COLORS,  default="#00ffff")
    weight = models.IntegerField(default=3, choices=WEIGHTS)




class GroupExtras(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, primary_key=True)
    airfield = models.OneToOneField(Airfield, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.FAAcode)


class Tails(models.Model):
    tail = models.CharField('Tail', max_length=15, primary_key=True)
    airfield = models.ForeignKey(Airfield, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return "callsign " + str(self.callsign) 


class AircraftType(models.Model):
    aircraftType = models.CharField('Type', max_length=20, primary_key=True, help_text="Must be valid ICAO type designator - see https://www.icao.int/publications/doc8643/pages/search.aspx for more info.")
    formationDistThreshold = models.DecimalField('Form Threshold (mi)', decimal_places=3, max_digits=8, default=2.0)
    formationLostSignalTimeThreshold = models.IntegerField('Lost Signal Time Threshold (sec)', default=15)
    fullStopThresholdSpeed = models.DecimalField('Full Stop Threshold (knots)', decimal_places=3, max_digits=8, default=70.0)
    rotateSpeed = models.DecimalField('Rotate Speed (knots)', decimal_places=3, max_digits=8, default=80.0)
    dualSortieTimeLimitHours = models.IntegerField(default=1)
    dualSortieTimeLimitMinutes = models.IntegerField(default=0)
    soloSortieTimeLimitHours = models.IntegerField(default=1)
    soloSortieTimeLimitMinutes = models.IntegerField(default=0)
    mapIconFile = models.ImageField(default='images/UFO.png', upload_to='images')
    lostSignalIconFile = models.ImageField(default='images/30-UFO.png', upload_to='images', help_text="Try using the map icon with this tool: https://onlinepngtools.com/change-png-opacity")
    soloIconFile = models.ImageField(null=True, blank=True, upload_to='images')
    troubleIconFile = models.ImageField(null=True, blank=True, upload_to='images')
    iconSize = models.IntegerField(default=20)


class RunwayManager(models.Manager):
    def getAllRunways():
        return list(Runway.objects.all())

CALLSIGN_TYPES = [('solo', 'solo'), ('form', 'form')]

class Callsign(models.Model):
    callsign = models.CharField('Callsign', max_length=20, primary_key=True)
    aircraftType = models.ForeignKey(AircraftType, null=True, blank=True, on_delete=models.CASCADE)
    type = models.CharField('Type', max_length=20, choices=CALLSIGN_TYPES, default="solo")


class Runway(models.Model):
    name = models.CharField('Name', max_length=15, primary_key=True, validators=[alphanumeric], help_text="Alphanumeric characters and _ only!")
    # primaryAircraftType = models.ForeignKey(AircraftType, on_delete=models.CASCADE, related_name='+')
    displayedAircraftTypes = models.ManyToManyField(AircraftType)
    airfield = models.ForeignKey(Airfield, on_delete=models.CASCADE)
    kmlPatternFile = models.FileField(null=True)
    patternAltitudeCeiling = models.IntegerField(null=True, blank=True)
    patternName = models.CharField("""Pattern Name """, max_length=30, null=True, help_text="""(e.g. "shoehorn"); this value must match the pattern placemark's 'name' tag value in the pattern file exactly (case sensitive!).""")
    class Meta:
        constraints = [models.UniqueConstraint(fields=["patternName"], name="patternName must be unique!")]

    def __str__(self):
        return str(self.name) 

class UserDisplayExtra(models.Model):
    runway = models.ForeignKey(Runway, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    additionalKML = models.ManyToManyField(AdditionalKML)
    class Meta:
        constraints = [ models.UniqueConstraint(fields=["runway", "user"], name="One runway per user")]


class RsuCrew(models.Model):
    runway = models.ForeignKey(Runway, on_delete=models.CASCADE, blank=True, null=True)
    controller = models.CharField('Controller', max_length=25, blank=True, null=True)
    observer = models.CharField('Observer', max_length=25, blank=True, null=True)
    spotter = models.CharField('Spotter', max_length=25, blank=True, null=True)
    recorder = models.CharField('Recorder', max_length=25, blank=True, null=True)
    timestamp = models.DateTimeField('Timestamp', blank=True, null=True)

    # def __str__(self):
    #     return "RSU Crew"

    def __str__(self):
        return "pattern point (lat,lon,alt): " + str(self.lat) + ", " + str(self.lon) + "," + str(self.alt)


class ActiveAircraftManager(models.Manager):

    def get_Acft_queryset_update_message(runway):
        """
        Return all active aircraft relevant to a particular runway crew, serialized
        """

        activeAcftquery = ActiveAircraft.objects.filter(Q(aircraftType__in=list(runway.displayedAircraftTypes.all())) | Q(substate=runway.patternName)).order_by('tailNumber')

        activeAcftMetadata = {}
        activeAcftMetadata['In_Pattern'] = activeAcftquery.filter(state='in pattern').filter(substate=runway.patternName).count() + activeAcftquery.filter(formationX2=True).filter(state='in pattern').filter(substate=runway.patternName).count() + activeAcftquery.filter(state='in pattern').filter(formationX4=True).filter(substate=runway.patternName).count()*3
        activeAcftMetadata['Taxiing'] = activeAcftquery.filter(state="taxiing").filter(substate=runway.patternName).count() + activeAcftquery.filter(formationX2=True).filter(substate=runway.patternName).filter(state="taxiing").count() + activeAcftquery.filter(formationX4=True).filter(substate=runway.patternName).filter(state="taxiing").count()*3
        activeAcftMetadata['Off_Station'] = activeAcftquery.filter(state="off station").count() + activeAcftquery.filter(formationX2=True).filter(state="off station").count() + activeAcftquery.filter(formationX4=True).filter(state="off station").count()*3
        activeAcftMetadata['Lost_Signal'] = activeAcftquery.filter(state="lost signal").count() + activeAcftquery.filter(formationX2=True).filter(state="lost signal").count() + activeAcftquery.filter(formationX4=True).filter(state="lost signal").count()*3

        activeAcftMetadata['dualLimit'] = []
        for acft in activeAcftquery.exclude(solo=True).exclude(state='taxiing'):
            if acft.takeoffTime is not None and acft.takeoffTime < timezone.now() - timedelta(hours=acft.aircraftType.dualSortieTimeLimitHours, minutes=acft.aircraftType.dualSortieTimeLimitMinutes):
                flightTime = timezone.now() - acft.takeoffTime
                activeAcftMetadata['dualLimit'].append(acft.callSign + "<br>" + str(flightTime)[:4])

        activeAcftMetadata['soloLimit'] = []
        for acft in activeAcftquery.filter(solo=True).exclude(state='taxiing'):
            if acft.takeoffTime is not None and acft.takeoffTime < timezone.now() - timedelta(hours=acft.aircraftType.soloSortieTimeLimitHours, minutes=acft.aircraftType.soloSortieTimeLimitMinutes):
                flightTime = timezone.now() - acft.takeoffTime
                activeAcftMetadata['soloLimit'].append(acft.callSign + "<br>" + str(flightTime)[:4])

        activeAcftMetadata['solosOffStation'] = []
        for acft in activeAcftquery.filter(solo=True).exclude(state='in pattern').exclude(state='taxiing'):
            activeAcftMetadata['solosOffStation'].append(acft.callSign)

        activeAcftMetadata['solosInPattern'] = []
        for acft in activeAcftquery.filter(solo=True).filter(state='in pattern'):
            activeAcftMetadata['solosInPattern'].append(acft.callSign)

        activeAcft = serializers.serialize('json', activeAcftquery)

        #logger.debug(json.dumps(activeAcftMetadata))
        return activeAcft, json.dumps(activeAcftMetadata)



class ActiveAircraft(models.Model):
    tailNumber = models.CharField('Tail', primary_key=True, max_length=15)
    # aircraftType = models.CharField('Type', max_length=20, blank=True, null=True)
    aircraftType = models.ForeignKey(AircraftType, on_delete=models.CASCADE, blank=True, null=True)
    callSign = models.CharField('Callsign', max_length=12, blank=True, null=True)
    takeoffTime = models.DateTimeField('Takeoff Time', blank=True, null=True)
    three55Code = models.CharField('355 Code', max_length=5, default='none')
    Comments = models.CharField('Comments', max_length=200, default='none')
    landTime = models.DateTimeField('Final Landing Time', blank=True, null=True)
    solo = models.BooleanField('Solo', default=False)
    formationX2 = models.BooleanField('2-Ship Form', default=False)
    formationX4 = models.BooleanField('4-Ship Form', default=False)
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
    state = models.CharField('State', max_length=20, blank=True, null=True)  # 'taxiiing', 'in pattern', 'off station', 'lost signal', or 'completed sortie'
    lastState = models.CharField('Last State', max_length=20, blank=True, null=True)  # 'taxiiing', 'in home pattern', 'off station', 'lost signal', or 'completed sortie'
    substate = models.CharField('Substate', max_length=20, blank=True, null=True) # used to discern specific pattern. Can be 'eastside', 'shoehorn', etc.
    homeField = models.ForeignKey(Airfield, on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField('Timestamp', blank=True, null=True)
    formTimestamp = models.DateTimeField('Form Timestamp', blank=True, null=True)
    wingman = models.CharField('Wingman', max_length=12, blank=True, null=True) # tail number of wingman

    def __str__(self):
        return "Tail " + str(self.tailNumber)

    

class CompletedSortie(models.Model):
    aircraftType = models.ForeignKey(AircraftType, on_delete=models.CASCADE, blank=True, null=True)
    tailNumber = models.CharField('Tail', max_length=15)
    callSign = models.CharField('Callsign', max_length=12, blank=True, null=True)
    takeoffTime = models.DateTimeField('Takeoff Time', blank=True, null=True)
    three55Code = models.CharField('355 Code', max_length=5, default='none')
    Comments = models.CharField('Comments', max_length=200, default='none')
    landTime = models.DateTimeField('Final Landing Time', blank=True, null=True)
    solo = models.BooleanField('Solo', default=False)
    formationX2 = models.BooleanField('2-Ship Form', default=False)
    formationX4 = models.BooleanField('4-Ship Form', default=False)
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
    lastState = models.CharField('Last State', max_length=20, blank=True, null=True)  # 'taxiiing', 'in home pattern', 'off station', 'lost signal', or 'completed sortie'
    substate = models.CharField('Substate', max_length=20, blank=True, null=True) # used to discern specific pattern. Can be 'eastside', 'shoehorn', etc.
    homeField = models.ForeignKey(Airfield, on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField('Timestamp', blank=True, null=True)
    formTimestamp = models.DateTimeField('Form Timestamp', blank=True, null=True)


    def __str__(self):
        return "id " + str(self.id)


class NextTakeoffData(models.Model):
    runway = models.OneToOneField(Runway, on_delete=models.CASCADE, blank=True, null=True)
    solo = models.BooleanField('Solo', default=False)
    formationX2 = models.BooleanField('2-Ship Form', default=False)
    formationX4 = models.BooleanField('4-Ship Form', default=False)

    def __str__(self):
        return "id " + str(self.id)



STATUS = [ ('Good', 'Good'), ('Medium', 'Medium'), ('Weak', 'Weak'), ('Inactive', 'Inactive')]
TRANSPORT = [ ('UDP', 'UDP'), ('TCP', 'TCP')]
PROTOCOL = [ ('GDL90', 'GDL90'), ('ASTERIX', 'ASTERIX')]
U_TYPE= [ ('Active', 'Active'), ('Passive', 'Passive')]
S_TYPE= [ ('Internet', 'Internet'), ('Local', 'Local'), ('Historical', 'Historical')]
class ADSBSource (models.Model):

    # User defined name for source
    name = models.CharField(max_length=50, default='ADS-B Source')

    # sourceType (Interernet, Local, Historical)
    sourceType=models.CharField(max_length=50, choices=S_TYPE,  default="Not selected")

    # Links to local reviever
    # IP port to initiate connection
    address = models.CharField(max_length=200, default='ws://192.168.10.1/traffic')
        # Request headers
    rapidAPIKey = models.CharField(max_length=257, blank=True, null=True)#PLACE ADSB EXCHANGE KEY HERE
    rapidAPIHost = models.CharField(max_length=257, default='adsbexchange-com1.p.rapidapi.com')
    miscURLValues = models.CharField(max_length=100, blank=True, null=True)#add extra info onto port and address
    # Connection info
        #Transport Layer and Protocol, Data parsing function (GDL90 or ASTRIX)  
    sourceStatus = models.CharField(max_length=50, choices=STATUS,  default="Inactive")
    transportLayer = models.CharField(max_length=50, choices=TRANSPORT,  default="Not selected")
    dataProtocol = models.CharField(max_length=50, choices=PROTOCOL,  default="Not selected")
    # confidenceScore in data source 1-ADSB Exchange 10-Eyeball of God. Weithgt fuction to determine how well its working -- manually adjusted for now, but will be adjusted with testing
    confidenceScore = models.IntegerField (default=0)
    lat = models.DecimalField('Latitude', blank=True, null=True, decimal_places=7, max_digits=10)
    lon = models.DecimalField('Longitude', blank=True, null=True, decimal_places=7, max_digits=10)
    alt = models.DecimalField('Field Elevation', decimal_places=3, max_digits=8, blank=True, null=True)
    radius = models.IntegerField (default=250)
    threadSwitch = models.BooleanField(default=False)
    # Passive(Constant data dump) or active(must be regularly requested)
    updateType=models.CharField(max_length=50, choices=U_TYPE,  default="Not selected")
    # activeUpdateFreq for active sources
    updateFreq=models.DecimalField(max_digits=10, default=1.0,decimal_places=3)#measured in seconds
    
class CommsControl(models.Model):
    Name = models.CharField(max_length=50, default="Comms Control")
    MessageThreadStatus = models.BooleanField(default=False)
    CommsManagementThreadStatus = models.BooleanField(default=False)
    ADSBProcessingThreadStatus = models.BooleanField(default=False)
    CommsControlKey = models.BooleanField(help_text="DO NOT CHANGE THIS VALUE UNLESS YOU KNOW WHAT YOU ARE DOING.", default=True, primary_key=True)

    def __str__(self):
        return "Comms Control"
