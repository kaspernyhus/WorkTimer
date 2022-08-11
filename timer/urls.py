from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('take_timestamp', views.new_timestamp, name='take_timestamp'),
    path('manual', views.manual_timestamp, name='manual_timestamp'),
    path('edit_day', views.edit_day, name='edit_day'),
    path('edit/<int:id>', views.edit_entry, name='edit_entry'),
    path('delete/<str:ids>', views.delete_entry_pair, name='delete'),
    path('week', views.show_week, name='show_week'),
    path('all_weeks', views.show_all_weeks, name='show_all_weeks'),

  ]