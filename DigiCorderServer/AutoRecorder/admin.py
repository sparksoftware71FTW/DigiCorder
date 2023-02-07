from django.contrib import admin

# Register your models here.
from .models import *

class ActiveAircraftAdmin(admin.ModelAdmin):
    list_display = ('aircraftType', 'tailNumber', 'callSign', 'state', 'lastState', 'solo', 'takeoffTime', 'three55Code', 'Comments', 'landTime', 'formationX2', 'formationX4','formTimestamp','timestamp', 'emergency', 'natureOfEmergency')
    list_filter = ['solo', 'emergency', 'takeoffTime', 'state', 'lastState']
admin.site.register(ActiveAircraft, ActiveAircraftAdmin)

class CompletedT6SortieAdmin(admin.ModelAdmin):
    list_display = ('aircraftType', 'tailNumber', 'callSign', 'solo', 'takeoffTime', 'three55Code', 'Comments', 'landTime', 'formationX2', 'formationX4','formTimestamp','timestamp', 'emergency', 'natureOfEmergency')
    list_filter = ['solo', 'emergency', 'takeoffTime', 'state', 'lastState']
admin.site.register(CompletedSortie, CompletedT6SortieAdmin)

class AircraftTypeAdmin(admin.ModelAdmin):
    list_display = ('aircraftType', 'formationDistThreshold', 'formationLostSignalTimeThreshold', 'fullStopThresholdSpeed', 'rotateSpeed')
    list_filter = ['aircraftType', 'formationDistThreshold', 'formationLostSignalTimeThreshold', 'fullStopThresholdSpeed', 'rotateSpeed']
admin.site.register(AircraftType , AircraftTypeAdmin)

class AdditionalKMLAdmin(admin.ModelAdmin):
    list_display = ('pk', 'file', 'color', 'weight')
    list_filter = ['file', 'color', 'weight']
admin.site.register(AdditionalKML, AdditionalKMLAdmin)

class RunwayAdmin(admin.ModelAdmin):
    list_display = ('name', 'airfield')
    list_filter = ['name', 'airfield']
admin.site.register(Runway, RunwayAdmin)

class RsuCrewAdmin(admin.ModelAdmin):
    list_display = ('id', 'runway', 'controller', 'observer', 'spotter', 'recorder', 'timestamp')
    list_filter = ['runway', 'controller', 'observer', 'spotter', 'recorder', 'timestamp']
admin.site.register(RsuCrew, RsuCrewAdmin)

class AirfieldAdmin(admin.ModelAdmin):
    list_display = ('FAAcode', 'name')
    list_filter = ['FAAcode', 'name']
admin.site.register(Airfield, AirfieldAdmin)

class NextTakeoffAdmin(admin.ModelAdmin):
    list_display = ('runway', 'solo', 'formationX2', 'formationX4')
    list_filter = ['runway', 'solo', 'formationX2', 'formationX4']
admin.site.register(NextTakeoffData, NextTakeoffAdmin)

class CallsignAdmin(admin.ModelAdmin):
    list_display = ('callsign', 'aircraftType', 'type')
    list_filter = ['callsign', 'aircraftType', 'type']
admin.site.register(Callsign, CallsignAdmin)

class UserDisplayExtraAdmin(admin.ModelAdmin):
    list_display = ('user','runway')
    # list_filter = ['user', ]
admin.site.register(UserDisplayExtra, UserDisplayExtraAdmin)