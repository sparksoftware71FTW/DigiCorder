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
from .models import ActiveAircraft, CompletedSortie, Airfield

# Create your views here.

def index(request):
    return render(request, 'AutoRecorder/bootbase.html')

@staff_member_required(login_url='AutoRecorder/bootbase.html')
def dashboard(request):
    return render(request, 'AutoRecorder/dashboard.html')


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


def toggleFormSolo(acft):
    if acft.formation == False:
        acft.formation = True
    elif acft.formation == True:
        acft.formation = False
    else:
        acft.formation = True

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