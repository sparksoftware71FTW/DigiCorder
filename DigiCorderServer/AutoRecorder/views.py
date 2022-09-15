from audioop import reverse
from re import template
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.db.models import F
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required



from .models import ActiveAircraft, CompletedSortie

# Create your views here.

def index(request):
    return render(request, 'AutoRecorder/bootbase.html')

@staff_member_required(login_url='/login')
def dashboard(request):
    return render(request, 'AutoRecorder/dashboard.html')

@staff_member_required(login_url='/login')
def form355(request):
    landedAircraft = CompletedSortie.objects.all()
    return render(request, 'AutoRecorder/form355.html', {"landedAircraft": landedAircraft})

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