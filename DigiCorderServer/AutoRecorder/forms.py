from django.forms import ModelForm
from .models import ActiveAircraft

class ActiveAircraft355(ModelForm):
    class Meta:
        model = ActiveAircraft
        fields = ['three55Code', 'Comments']
        