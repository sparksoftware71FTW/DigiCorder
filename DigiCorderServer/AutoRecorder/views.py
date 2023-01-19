from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.db.models import F, Q
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.template.context_processors import csrf
from django.forms import modelform_factory, formset_factory, SelectDateWidget
from crispy_forms.utils import render_crispy_form

from .forms import Form355Filters, Form355FiltersFormsetHelper
from .models import ActiveAircraft, CompletedSortie, Airfield, RsuCrew, Runway

# Create your views here.

def index(request):
    return render(request, 'AutoRecorder/bootbase.html')

@staff_member_required(login_url='/AutoRecorder')
def dashboard(request):
    RsuCrewFormFactory = modelform_factory(model=RsuCrew, exclude=('timestamp',))
    if request.method == 'POST':
        crew = RsuCrew.objects.create(timestamp=timezone.now())
        crewformset = RsuCrewFormFactory(request.POST, instance=crew)
        if crewformset.is_valid():
            crewformset.timestamp = timezone.now()
            crewformset.save()
            return HttpResponseRedirect(reverse('AutoRecorder:dashboard'))
    else:
        try:
            crew = RsuCrew.objects.latest('timestamp')
            print(str(crew.controller) + "!!!!!!")
        except RsuCrew.DoesNotExist:
            crew = RsuCrew.objects.create(timestamp=timezone.now())
            print(str(crew.controller) + "Created initial blank RSU Crew!!!!")

        crewformset = RsuCrewFormFactory(instance=crew)
        runways = list(Runway.objects.all())
        return render(request, 'AutoRecorder/dashboardNew.html', {"crewformset": crewformset, "runways": runways[0]})
    #return render(request, 'AutoRecorder/dashboard.html')


@staff_member_required(login_url='/AutoRecorder')
def form355(request):
    landedAircraft = CompletedSortie.objects.all().order_by('timestamp')
    RSUcrews = RsuCrew.objects.all().order_by('timestamp')
    runways = Runway.objects.all()
    rwys = []
    acft_types = []
    oldest_entry = None
    newest_entry = None
    for acft in landedAircraft:

        if oldest_entry is None or acft.timestamp is not None and acft.timestamp < oldest_entry:
            oldest_entry = acft.timestamp

        if newest_entry is None or acft.timestamp is not None and acft.timestamp > newest_entry:
            newest_entry = acft.timestamp

        if (acft.aircraftType, acft.aircraftType) not in acft_types:
            acft_types.append((acft.aircraftType, acft.aircraftType))
    
    if oldest_entry == None:
        oldest_entry = timezone.now()
    if newest_entry == None:
        newest_entry = timezone.now()

    for rwy in runways:
        if (rwy.name, rwy.name) not in rwys:
            rwys.append((rwy.name, rwy.name))

    form355FilterFormset = formset_factory(Form355Filters)
    helper = Form355FiltersFormsetHelper()

    if request.method == 'POST':
        formset = form355FilterFormset(request.POST)
        for form in formset:
            form.fields['acftType'].choices = acft_types
            form.fields['fromDate'].widget = SelectDateWidget(years=range(oldest_entry.year, newest_entry.year + 1), empty_label=("Year", "Month", "Day"))
            form.fields['toDate'].widget = SelectDateWidget(years=range(oldest_entry.year, newest_entry.year + 1), empty_label=("Year", "Month", "Day"))
            form.fields['runway'].choices = rwys
            form = render_crispy_form(form)
        if formset.is_valid():
            print(formset.cleaned_data[0]['acftType'])
            data = formset.cleaned_data[0]

            qAcftFilter = Q()
            qAcftExclude = Q()
            qRSUCrewSearch = Q()
            if data['gotNailed']:
                qAcftExclude &= Q(three55Code="none")
                print(qAcftExclude)
            if data['callSign'] is not None:
                qAcftFilter &= Q(callSign__contains=data['callSign'])
                print(qAcftFilter)
            if data['search'] != '':
                print(data['search'])
                qRSUCrewSearch |= Q(controller__contains=data['search'])
                qRSUCrewSearch |= Q(observer__contains=data['search'])
                qRSUCrewSearch |= Q(spotter__contains=data['search'])
                qRSUCrewSearch |= Q(recorder__contains=data['search'])
                print(qRSUCrewSearch)

            return render(request, 'AutoRecorder/form355.html', 
            {"landedAircraft": landedAircraft.filter(aircraftType=data['acftType']).filter(qAcftFilter).exclude(
                qAcftExclude).exclude(timestamp__lt=data['fromDate']).exclude(timestamp__gt=data['toDate']),
             "formset": formset, 
             "RSUcrews": RSUcrews.filter(qRSUCrewSearch).exclude(
                timestamp__lt=data['fromDate']).exclude(timestamp__gt=data['toDate'])})
        else:
            return render(request, 'AutoRecorder/form355.html', {"landedAircraft": landedAircraft, "formset": formset, "RSUcrews": RSUcrews})
    
    else:
        formset = form355FilterFormset()
        for form in formset:
            form.fields['acftType'].choices = acft_types
            form.fields['fromDate'].widget = SelectDateWidget(years=range(oldest_entry.year, newest_entry.year + 1), empty_label=("Year", "Month", "Day"))
            print(range(oldest_entry.year, newest_entry.year))
            form.fields['toDate'].widget = SelectDateWidget(years=range(oldest_entry.year, newest_entry.year + 1), empty_label=("Year", "Month", "Day"))
            form = render_crispy_form(form)
        
        return render(request, 'AutoRecorder/form355.html', {"landedAircraft": landedAircraft, "formset": formset, "RSUcrews": RSUcrews})


@staff_member_required(login_url='/AutoRecorder')
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


@staff_member_required(login_url='/AutoRecorder')
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


@staff_member_required(login_url='/AutoRecorder')
def formSolo(request, tailNumber):

    if request.method == 'POST':
        acft = get_object_or_404(ActiveAircraft, pk=tailNumber)
        toggleFormSolo(acft)
        return HttpResponseRedirect(reverse('AutoRecorder:dashboard'))
    else:
        return render(request, 'AutoRecorder/dashboard.html')


@staff_member_required(login_url='/AutoRecorder')
def formX2(request, tailNumber):

    if request.method == 'POST':
        acft = get_object_or_404(ActiveAircraft, pk=tailNumber)
        toggleFormX2(acft)
        return HttpResponseRedirect(reverse('AutoRecorder:dashboard'))
    else:
        return render(request, 'AutoRecorder/dashboard.html')


@staff_member_required(login_url='/AutoRecorder')
def formX4(request, tailNumber):

    if request.method == 'POST':
        acft = get_object_or_404(ActiveAircraft, pk=tailNumber)
        toggleFormX4(acft)
        return HttpResponseRedirect(reverse('AutoRecorder:dashboard'))
    else:
        return render(request, 'AutoRecorder/dashboard.html')


@staff_member_required(login_url='/AutoRecorder')
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