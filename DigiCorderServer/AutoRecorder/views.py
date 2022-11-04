from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.db.models import F
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.forms import modelform_factory

from . import forms
from .models import ActiveAircraft, CompletedSortie, Airfield, RSUcrew

# Create your views here.

def index(request):
    return render(request, 'AutoRecorder/bootbase.html')

@staff_member_required(login_url='AutoRecorder/bootbase.html')
def dashboard(request):
    RSUcrewFormFactory = modelform_factory(model=RSUcrew, exclude=('timestamp',))
    if request.method == 'POST':
        crew = RSUcrew.objects.create(timestamp=timezone.now())
        crewformset = RSUcrewFormFactory(request.POST, instance=crew)
        if crewformset.is_valid():
            crewformset.timestamp = timezone.now()
            crewformset.save()
            return HttpResponseRedirect(reverse('AutoRecorder:dashboard'))
    else:
        try:
            crew = RSUcrew.objects.latest('timestamp')
            print(str(crew.controller) + "!!!!!!")
        except RSUcrew.DoesNotExist:
            crew = RSUcrew.objects.create(timestamp=timezone.now())
            print(str(crew.controller) + "Created initial blank RSU Crew!!!!")

        crewformset = RSUcrewFormFactory(instance=crew)
        return render(request, 'AutoRecorder/dashboard.html', {"crewformset": crewformset})
    #return render(request, 'AutoRecorder/dashboard.html')


@staff_member_required(login_url='AutoRecorder/bootbase.html')
def form355(request):
    landedAircraft = CompletedSortie.objects.all()
    return render(request, 'AutoRecorder/form355.html', {"landedAircraft": landedAircraft})


@staff_member_required(login_url='/login')
def violation355View(request, tailNumber):
    acft = get_object_or_404(ActiveAircraft, pk=tailNumber)
    #acft355 = forms.ActiveAircraft355(instance=ActiveAircraft.objects.get(tailNumber=tailNumber))
    Acft355FormFactory = modelform_factory(model=ActiveAircraft, fields=('three55Code', 'Comments'), help_texts=('Burger King is always hiring...',''))

    if request.method == 'POST':
        acft355formset = Acft355FormFactory(request.POST, instance=acft)
        if acft355formset.is_valid():
            acft355formset.save()
            return HttpResponseRedirect(reverse('AutoRecorder:dashboard'))
    else:
        acft355formset = Acft355FormFactory(instance=acft)
        return render(request, 'AutoRecorder/edit355.html', {"acft355formset": acft355formset})


@staff_member_required(login_url='/login')
def editView(request, tailNumber):
    acft = get_object_or_404(ActiveAircraft, pk=tailNumber)
    #acft355 = forms.ActiveAircraft355(instance=ActiveAircraft.objects.get(tailNumber=tailNumber))
    AcftFormFactory = modelform_factory(model=ActiveAircraft, exclude=('tailNumber',))

    if request.method == 'POST':
        acfteditformset = AcftFormFactory(request.POST, instance=acft)
        if acfteditformset.is_valid():
            acfteditformset.save()
            return HttpResponseRedirect(reverse('AutoRecorder:dashboard'))
    else:
        acfteditformset = AcftFormFactory(instance=acft)
        return render(request, 'AutoRecorder/edit.html', {"acfteditformset": acfteditformset})


@staff_member_required(login_url='AutoRecorder/bootbase.html')
def formSolo(request, tailNumber):

    if request.method == 'POST':
        acft = get_object_or_404(ActiveAircraft, pk=tailNumber)
        toggleFormSolo(acft)
        return HttpResponseRedirect(reverse('AutoRecorder:dashboard'))
    else:
        return render(request, 'AutoRecorder/dashboard.html')


@staff_member_required(login_url='AutoRecorder/bootbase.html')
def formX2(request, tailNumber):

    if request.method == 'POST':
        acft = get_object_or_404(ActiveAircraft, pk=tailNumber)
        toggleFormX2(acft)
        return HttpResponseRedirect(reverse('AutoRecorder:dashboard'))
    else:
        return render(request, 'AutoRecorder/dashboard.html')


@staff_member_required(login_url='AutoRecorder/bootbase.html')
def formX4(request, tailNumber):

    if request.method == 'POST':
        acft = get_object_or_404(ActiveAircraft, pk=tailNumber)
        toggleFormX4(acft)
        return HttpResponseRedirect(reverse('AutoRecorder:dashboard'))
    else:
        return render(request, 'AutoRecorder/dashboard.html')


@staff_member_required(login_url='AutoRecorder/bootbase.html')
def solo(request, tailNumber):

    if request.method == 'POST':
        acft = get_object_or_404(ActiveAircraft, pk=tailNumber)
        toggleSolo(acft)
        return HttpResponseRedirect(reverse('AutoRecorder:dashboard'))
    else:
        return render(request, 'AutoRecorder/dashboard.html')


def toggleFormSolo(acft):
    if acft.formationX2 == False:
        acft.formationX2 = True
    elif acft.formationX2 == True:
        acft.formationX2 = False
    else:
        acft.formationX2 = True

    if acft.solo == False:
        acft.solo = True
    elif acft.solo == True:
        acft.solo = False
    else:
        acft.solo = True

    acft.save()


def toggleFormX2(acft):
    if acft.formationX2 == False:
        acft.formationX2 = True
    elif acft.formationX2 == True:
        acft.formationX2 = False
    else:
        acft.formationX2 = True
    acft.save()


def toggleFormX4(acft):
    if acft.formationX4 == False:
        acft.formationX4 = True
    elif acft.formationX4 == True:
        acft.formationX4 = False
    else:
        acft.formationX4 = True
    acft.save()


def toggleSolo(acft):
    if acft.solo == False:
        acft.solo = True
    elif acft.solo == True:
        acft.solo = False
    else:
        acft.solo = True
    acft.save()

# class IndexView(generic.ListView):
#     template_name = 'AutoRecorder/index.html'
#     context_object_name = 'latest_ActiveAircraft_list'

#     def get_queryset(self):
#         """
#         Return all active T-6s
#         """
#         #Question.objects.filter(pub_date__lte=timezone.now())
#         return ActiveAircraft.objects.filter(takeoffTime__lte=timezone.now()).order_by(
#        '-takeoffTime')[:]