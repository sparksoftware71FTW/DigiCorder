from audioop import reverse
from re import template
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.db.models import F
from django.views import generic
from django.utils import timezone

from .models import Active_T6, Completed_T6_Sortie

# Create your views here.

def index(request):
    return HttpResponse("Hello, world. AutoRecorder Temp Index is here!")

def dashboard(request):
    return render(request, 'AutoRecorder/dashboard.html')

def form355(request):
    landedAircraft = Completed_T6_Sortie.objects.all()
    return render(request, 'AutoRecorder/form355.django-html', {"landedAircraft": landedAircraft})

# class IndexView(generic.ListView):
#     template_name = 'AutoRecorder/index.html'
#     context_object_name = 'latest_active_t6_list'

#     def get_queryset(self):
#         """
#         Return all active T-6s
#         """
#         #Question.objects.filter(pub_date__lte=timezone.now())
#         return Active_T6.objects.filter(takeoffTime__lte=timezone.now()).order_by(
#        '-takeoffTime')[:]