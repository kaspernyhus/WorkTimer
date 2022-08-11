from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('take_timestamp', views.new_timestamp, name='take_timestamp'),
    path('manual', views.manual_timestamp, name='manual_timestamp'),
    path('week', views.show_week, name='show_week'),
    path('all_weeks', views.show_all_weeks, name='show_all_weeks'),
  ]