from django.db import models
from django.utils import timezone
from django.contrib import admin

import datetime


# Create your models here.
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    @admin.display(
            boolean=True,
            ordering='pub_date',
            description='Published recently?',
        )

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Choice(models.Model):
    question = models.ForeignKey(Question,
    on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

class T6(models.Model):
    tailNumber = models.IntegerField('Tail Number')
    callSign = models.CharField('Callsign', max_length=12)
    takeoffTime = models.DateTimeField('Initial Takeoff Time')
    landTime = models.DateTimeField('Final Landing Time')
    three55 = models.CharField('355 Comments', max_length=100, default='none')
    solo = models.BooleanField('Solo', default=False)
    formation = models.BooleanField('Formation', default=False)
    crossCountry = models.BooleanField('X-Country', default=False)
    localFlight = models.BooleanField('LocalFlight', default=True)
    inEastsidePattern = models.BooleanField('Currently in Eastside Pattern', default=True)
    emergency = models.BooleanField('Emergency', default=False)
    natureOfEmergency = models.CharField('Nature of Emergency:', max_length=200)


