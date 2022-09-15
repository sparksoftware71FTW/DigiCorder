from django.contrib import admin

# Register your models here.
from .models import ActiveAircraft, CompletedSortie

class ActiveAircraftAdmin(admin.ModelAdmin):
    list_display = ('aircraftType', 'tailNumber', 'callSign', 'state', 'lastState', 'solo', 'takeoffTime', 'three55Code', 'Comments', 'landTime', 'formation', 'emergency', 'natureOfEmergency')
    list_filter = ['solo', 'emergency', 'takeoffTime']
admin.site.register(ActiveAircraft, ActiveAircraftAdmin)

class CompletedT6SortieAdmin(admin.ModelAdmin):
    list_display = ('aircraftType', 'tailNumber', 'callSign', 'solo', 'takeoffTime', 'three55Code', 'Comments', 'landTime', 'formation', 'emergency', 'natureOfEmergency')
    list_filter = ['solo', 'emergency', 'takeoffTime']
admin.site.register(CompletedSortie, CompletedT6SortieAdmin)
