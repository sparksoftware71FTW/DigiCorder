from django.urls import path, include
from . import views

app_name = 'AutoRecorder'
urlpatterns = [
    #path('', views.IndexView.as_view(), name='index'),
    path('', views.index, name='index'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('form355', views.form355, name='form355'),
    path('dashboard/355/<str:tailNumber>', views.violation355View, name='violation355View'),
    path('dashboard/edit/<str:tailNumber>', views.editView, name='editView'),
    path('dashboard/formsolo/<str:tailNumber>', views.formSolo, name='formSolo')

]