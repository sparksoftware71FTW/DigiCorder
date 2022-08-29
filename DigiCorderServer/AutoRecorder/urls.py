from django.urls import path, include
from . import views

app_name = 'AutoRecorder'
urlpatterns = [
    #path('', views.IndexView.as_view(), name='index'),
    path('', views.index, name='index'),
    path('dashboard', views.dashboard, name='dashboard')

]