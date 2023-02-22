from django.urls import path, include
from . import views
#The urls.py file is used to map URLs to a particular view function.

app_name = 'AutoRecorder'
urlpatterns = [
    #path('', views.IndexView.as_view(), name='index'),
    path('', views.index, name='index'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('form355', views.form355, name='form355'),
    path('dashboard/355/<str:tailNumber>', views.violation355View, name='violation355View'),
    path('dashboard/edit/<str:tailNumber>', views.editView, name='editView'),
    # path('dashboard/formsolo/<str:tailNumber>', views.formSolo, name='formSolo'),
    path('dashboard/<str:airfield>/<str:runway>/formX2/<str:tailNumber>', views.formX2, name='formX2'),
    path('dashboard/<str:airfield>/<str:runway>/formX4/<str:tailNumber>', views.formX4, name='formX4'),
    path('dashboard/<str:airfield>/<str:runway>/solo/<str:tailNumber>', views.solo, name='solo'),
    path('dashboard/<str:airfield>/<str:runway>', views.runway, name='runway')
]