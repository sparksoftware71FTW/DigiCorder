from django.contrib import admin

# Register your models here.
from .models import Active_T6, Completed_T6_Sortie

class ActiveT6Admin(admin.ModelAdmin):

    list_display = ('tailNumber', 'callSign', 'solo', 'takeoffTime', 'three55Code', 'Comments', 'landTime', 'formation', 'crossCountry', 'inEastsidePattern', 'emergency', 'natureOfEmergency')
    list_filter = ['inEastsidePattern', 'solo', 'emergency', 'takeoffTime']
admin.site.register(Active_T6, ActiveT6Admin)

#admin.site.register(Active_T6)
admin.site.register(Completed_T6_Sortie)
