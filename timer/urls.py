from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('take_timestamp', views.new_timestamp, name='take_timestamp')
  ]