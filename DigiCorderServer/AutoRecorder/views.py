from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.db.models import F, Q
from django.views import generic
from django.utils import timezone
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.template.context_processors import csrf
from django.forms import modelform_factory, formset_factory, SelectDateWidget
from crispy_forms.utils import render_crispy_form
from django.core.exceptions import ObjectDoesNotExist
from .forms import Form355Filters, Form355FiltersFormsetHelper
from .models import ActiveAircraft, CompletedSortie, Airfield, RsuCrew, Runway
import traceback

import logging
logger = logging.getLogger(__name__)

# Create your views here.

# The views.py files are the main files that handle the logic for the web application. They take in the user's input and generate the appropriate output based on a given input.
# The index function is the main function for the home page. It takes in the user's input from the database and generates the information for the home page.

def index(request):
    try:
        return render(request, 'AutoRecorder/bootbase.html')
    except:
        logger.error("Error in Index Function")
        logger.error(traceback.format_exc())

# @staff_member_required(login_url='/AutoRecorder')
# def runway(request):
#     RsuCrewFormFactory = modelform_factory(model=RsuCrew, exclude=('timestamp',))
#     if request.method == 'POST':
#         crew = RsuCrew.objects.create(timestamp=timezone.now())
#         crewformset = RsuCrewFormFactory(request.POST, instance=crew)
#         if crewformset.is_valid():
#             crewformset.timestamp = timezone.now()
#             crewformset.save()
#             return HttpResponseRedirect(reverse('AutoRecorder:dashboard'))
#     else:
#         try:
#             crew = RsuCrew.objects.latest('timestamp')
#             print(str(crew.controller) + "!!!!!!")
#         except RsuCrew.DoesNotExist:
#             crew = RsuCrew.objects.create(timestamp=timezone.now())
#             print(str(crew.controller) + "Created initial blank RSU Crew!!!!")

#         crewformset = RsuCrewFormFactory(instance=crew)
#         runways = list(Runway.objects.all())
#         return render(request, 'AutoRecorder/dashboardNew.html', {"crewformset": crewformset, "runways": runways[0]})


@staff_member_required(login_url='/AutoRecorder')
def runway(request, airfield, runway):
    try:
        airfields = []
        runways = []
        rejectRequest = True # Make sure this user is actually a member of the authorized users group...

        #Get all the airfields and the associated runway objects that a user has access to...
        for group in request.user.groups.all():
            if hasattr(group, 'airfield'):
                airfields.append(group.airfield)
                if group.airfield.FAAcode == airfield:
                    rejectRequest = False
        
        # if the user was not in the requested airfield's associated group, serve them a 404
        if rejectRequest is True:
            logger.info("User not in the requested airfield's associated group")
            raise Http404
        
        else:
            # otherwise, serve all runways that the user has access to
            for field in airfields:
                for rwy in Runway.objects.filter(airfield=field):
                    runways.append(rwy)
            logger.debug(runways)
            RsuCrewFormFactory = modelform_factory(model=RsuCrew, exclude=('timestamp','endTime', 'trafficCount'))

            try:
                field = Airfield.objects.get(FAAcode=airfield)
                displayedRunwayObject = Runway.objects.get(name=runway)
                displayedAcftTypes = serializers.serialize('json', displayedRunwayObject.displayedAircraftTypes.all())
                displayExtras = request.user.userdisplayextra_set.get(runway__name=runway)
                additionalKML = list(displayExtras.additionalKML.all())

            except ObjectDoesNotExist:
                logger.info("ObjectDoesNotExist in Runway Function (one or multiple of airfield, runway, aircraft type, display extras, or additional KML objects)")
                raise Http404

            if request.method == 'POST':
                crew = RsuCrew.objects.create(timestamp=timezone.now())
                crewformset = RsuCrewFormFactory(request.POST, instance=crew)
                if crewformset.is_valid():
                    crewformset.timestamp = timezone.now()
                    crewformset.save()
                    return HttpResponseRedirect(reverse('AutoRecorder:runway', args=(airfield, runway)))
            else:
                try:
                    crew = RsuCrew.objects.filter(runway=displayedRunwayObject).latest('timestamp')
                except RsuCrew.DoesNotExist:
                    crew = RsuCrew.objects.create(timestamp=timezone.now(), runway=displayedRunwayObject)

                crewformset = RsuCrewFormFactory(instance=crew)
            
                return render(request, 'AutoRecorder/runwayDisplay.html', {"crewformset": crewformset,
                "runways": runways, "runway": runway, "host": request.get_host(), "field": field,
                "displayedAcftTypes": displayedAcftTypes, "displayedRunwayObject": displayedRunwayObject,
                "additionalKML": additionalKML})
    except:
        logger.error("Error in Runway Function")
        logger.error(traceback.format_exc())


@staff_member_required(login_url='/AutoRecorder')
def dashboard(request):
    try:
        airfields = []
        runways = []
        #Get all the airfields and the associated runway objects that a user has access to...
        for group in request.user.groups.all():
            if hasattr(group, 'airfield'):
                airfields.append(group.airfield)
        for airfield in airfields:
            for runway in Runway.objects.filter(airfield=airfield):
                runways.append(runway)
        
        return render(request, 'AutoRecorder/dashboardNew.html', {"runways": runways, "host": request.get_host()})
        #return render(request, 'AutoRecorder/dashboard.html')
    except:
        logger.error("Error in Dashboard Function")
        logger.error(traceback.format_exc())


# The form355 function is the main function for the Form 355 report. It takes in the user's input from the frontend, hits the database, and generates the information for the report.
@staff_member_required(login_url='/AutoRecorder')
def form355(request):
    try:
        # Load necessary objects and empty lists
        landedAircraft = CompletedSortie.objects.all().order_by('timestamp')
        RSUcrews = RsuCrew.objects.all().order_by('timestamp')
        runways = Runway.objects.all()
        rwys = []
        acft_types = []
        oldest_entry = None
        newest_entry = None
        
        # Get the oldest and newest timestamp from the completedSortie objects
        for acft in landedAircraft:

            if oldest_entry is None or acft.timestamp is not None and acft.timestamp < oldest_entry:
                oldest_entry = acft.timestamp

            if newest_entry is None or acft.timestamp is not None and acft.timestamp > newest_entry:
                newest_entry = acft.timestamp

            if (acft.aircraftType.aircraftType, acft.aircraftType.aircraftType) not in acft_types:
                acft_types.append((acft.aircraftType.aircraftType, acft.aircraftType.aircraftType))
        
        # If there are no entries in the database, set the oldest and newest entries to the current time
        if oldest_entry == None:
            oldest_entry = timezone.now()
        if newest_entry == None:
            newest_entry = timezone.now()

        # Build a list of runways from the runway objects
        for rwy in runways:
            if (rwy.name, rwy.name) not in rwys:
                rwys.append((rwy.name, rwy.name))
        rwys.append(('',''))

        # Create formset factory and helper
        form355FilterFormset = formset_factory(Form355Filters)
        helper = Form355FiltersFormsetHelper()

        # Check if the request method is POST and process the submitted form data
        if request.method == 'POST':
            formset = form355FilterFormset(request.POST)
            # Set field choices from the form data fields
            for form in formset:
                form.fields['acftType'].choices = acft_types
                form.fields['fromDate'].widget = SelectDateWidget(years=range(oldest_entry.year, newest_entry.year + 1), empty_label=("Year", "Month", "Day"))
                form.fields['toDate'].widget = SelectDateWidget(years=range(oldest_entry.year, newest_entry.year + 1), empty_label=("Year", "Month", "Day"))
                form.fields['runway'].choices = rwys
                form = render_crispy_form(form)

            # Filter the querysets and render the template with the filtered data
            if formset.is_valid():
                logger.debug("Formset Cleaned Data (Position 0): " + str(formset.cleaned_data[0]))
                data = formset.cleaned_data[0]

                # Create query set filters based on filtered fields
                qAcftFilter = Q()
                qAcftExclude = Q()
                qRSUCrewSearch = Q()
                qRunwayFilter = Q()
                qPatternNameFilter = Q()
                if data['gotNailed']:
                    qAcftExclude &= Q(three55Code="none")
                    logger.debug("Got Nailed, so applied qAcftExclude filter to filter by 'none' 355 code (in Form355 function), following filter applied:" + str(qAcftExclude))
                if data['callSign'] is not None:
                    qAcftFilter &= Q(callSign__contains=data['callSign'])
                    logger.debug("Call Sign exists, so qAcftFilter applied to filter by call sign (in Form355 function), following filter applied:" + str(qAcftFilter))
                if data['search'] != '':
                    logger.debug("Search field exists, so qRSUCrewSearch applied to filter by search field (in Form355 function), following was searched:" + str(data['search']))
                    qRSUCrewSearch |= Q(controller__contains=data['search'])
                    qRSUCrewSearch |= Q(observer__contains=data['search'])
                    qRSUCrewSearch |= Q(spotter__contains=data['search'])
                    qRSUCrewSearch |= Q(recorder__contains=data['search'])
                logger.debug("Search Criteria (in Form355 function):" + qRSUCrewSearch)

                # Create cases for runway name filtering
                if data['runway'] != '':
                    runway = Runway.objects.get(name=data['runway'])
                    qRunwayFilter &= Q(runway__name__exact=runway.name)
                    qAcftFilter &= Q(substate__exact=runway.patternName)
                logger.debug("Aircraft Filter Applied: " + str(qAcftFilter))
                
                return render(request, 'AutoRecorder/form355.html', 
                {"landedAircraft": landedAircraft.filter(aircraftType__aircraftType__exact=data['acftType']).filter(qAcftFilter).exclude(
                    qAcftExclude).exclude(timestamp__lt=data['fromDate']).exclude(timestamp__gt=data['toDate']),  # excludes entries before the FromDate and after the ToDate
                "formset": formset, 
                "RSUcrews": RSUcrews.filter(qRSUCrewSearch).exclude(
                    timestamp__lt=data['fromDate']).exclude(timestamp__gt=data['toDate']).filter(qRunwayFilter)})
            else:
                return render(request, 'AutoRecorder/form355.html', {"landedAircraft": landedAircraft, "formset": formset, "RSUcrews": RSUcrews}) # render the response without the filter values
        
        else:
            formset = form355FilterFormset()
            for form in formset: # loop over each form in the formset
                form.fields['acftType'].choices = acft_types # sets choices based on the AircraftTypes currently in the database
                form.fields['fromDate'].widget = SelectDateWidget(years=range(oldest_entry.year, newest_entry.year + 1), empty_label=("Year", "Month", "Day")) # creates widget for the FromDate field to pick dates between the oldest and newest entry in the database
                logger.debug("Range of years (in Form355 function): " + str(range(oldest_entry.year, newest_entry.year + 1)))
                form.fields['toDate'].widget = SelectDateWidget(years=range(oldest_entry.year, newest_entry.year + 1), empty_label=("Year", "Month", "Day")) # creates widget for the ToDate field to pick dates between the oldest and newest entry in the database
                form.fields['runway'].choices = rwys # sets the choices for the runway field to be the available runways
                form = render_crispy_form(form) # renders the form in crispy format
            
            return render(request, 'AutoRecorder/form355.html', {"landedAircraft": landedAircraft, "formset": formset, "RSUcrews": RSUcrews}) # renders the template with the formset and the querysets
    except:
        logger.error("Error in form355 Function")
        logger.error(traceback.format_exc())


#the violation355View function is called when the user clicks the "355" button on the dashboard page. It takes the tail number of the aircraft as a parameter and returns a form to edit the 355 code and comments for that aircraft.
@staff_member_required(login_url='/AutoRecorder')
def violation355View(request, tailNumber):
    try:
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
    except:
        logger.error("Error in violation355View Function")
        logger.error(traceback.format_exc())


# The editView function is called when the user clicks the "edit" button on the dashboard page, and gives the user a form to edit the data associated with a particular active aircraft.
@staff_member_required(login_url='/AutoRecorder')
def editView(request, tailNumber):
    try:
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
            runways = Runway.objects.all()           
            return render(request, 'AutoRecorder/edit.html', {"acfteditformset": acfteditformset, "runways": runways})
    except:
        logger.error("Error in editView Function")
        logger.error(traceback.format_exc())


#the formSolo function is called when the user clicks the "Solo" button on the dashboard. It takes the tail number of the aircraft as a parameter and returns a form to edit the solo status for that aircraft.
# @staff_member_required(login_url='/AutoRecorder')
# def formSolo(request, tailNumber):

#     if request.method == 'POST':
#         acft = get_object_or_404(ActiveAircraft, pk=tailNumber)
#         toggleFormSolo(acft)
#         return HttpResponseRedirect(reverse('AutoRecorder:dashboard'))
#     else:
#         return render(request, 'AutoRecorder/dashboard.html')

#the formX2 function is called when the user clicks the "2-Ship" checkbox on the dashboard. It takes the tail number of the aircraft as a parameter and toggles their 2-ship formation state.
@staff_member_required(login_url='/AutoRecorder')
def formX2(request, airfield, runway, tailNumber):
    try:
        if request.method == 'POST':
            acft = get_object_or_404(ActiveAircraft, pk=tailNumber)
            toggleFormX2(acft)
            return HttpResponseRedirect(reverse('AutoRecorder:runway', args=[airfield, runway]))
        else:
            return render(request, 'AutoRecorder/dashboard.html')
    except:
        logger.error("Error in formX2 Function")
        logger.error(traceback.format_exc())


#the formX2 function is called when the user clicks the "4-Ship" checkbox on the dashboard. It takes the tail number of the aircraft as a parameter and toggles their 4-ship formation state.
@staff_member_required(login_url='/AutoRecorder')
def formX4(request, airfield, runway, tailNumber):
    try:
        if request.method == 'POST':
            acft = get_object_or_404(ActiveAircraft, pk=tailNumber)
            toggleFormX4(acft)
            return HttpResponseRedirect(reverse('AutoRecorder:runway', args=[airfield, runway]))
        else:
            return render(request, 'AutoRecorder/dashboard.html')
    except:
        logger.error("Error in formX4 Function")
        logger.error(traceback.format_exc())


#the solo function is called when the user clicks the "Solo" button on the runway dashboard page. It takes the tail number of the aircraft as a parameter and marks that aircraft as a solo in the database.
@staff_member_required(login_url='/AutoRecorder')
def solo(request, airfield, runway, tailNumber):
    try:
        if request.method == 'POST':
            acft = get_object_or_404(ActiveAircraft, pk=tailNumber)
            toggleSolo(acft)
            return HttpResponseRedirect(reverse('AutoRecorder:runway', args=[airfield, runway]))
        else:
            return render(request, 'AutoRecorder/dashboard.html')
    except:
        logger.error("Error in solo Function")
        logger.error(traceback.format_exc())


#the following functions change the state of the solo, 2-ship, and 4-ship attributes of active aircraft as a result of clicking the buttons on the runway dashboard pages.
def toggleFormSolo(acft):
    try:
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
    except:
        logger.error("Error in toggleFormSolo Function")
        logger.error(traceback.format_exc())


def toggleFormX2(acft):
    try:
        if acft.formationX2 == False:
            acft.formationX2 = True
        elif acft.formationX2 == True:
            acft.formationX2 = False
        else:
            acft.formationX2 = True
        acft.save()
    except:
        logger.error("Error in toggleFormX2 Function")
        logger.error(traceback.format_exc())


def toggleFormX4(acft):
    try:
        if acft.formationX4 == False:
            acft.formationX4 = True
        elif acft.formationX4 == True:
            acft.formationX4 = False
        else:
            acft.formationX4 = True
        acft.save()
    except:
        logger.error("Error in toggleFormX4 Function")
        logger.error(traceback.format_exc())


def toggleSolo(acft):
    try:
        if acft.solo == False:
            acft.solo = True
        elif acft.solo == True:
            acft.solo = False
        else:
            acft.solo = True
        acft.save()
    except:
        logger.error("Error in toggleSolo Function")
        logger.error(traceback.format_exc())


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