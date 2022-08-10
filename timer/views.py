from cmath import nan
from time import time
from django.shortcuts import render, redirect
from .models import *
from datetime import datetime, timedelta


def get_day_data(date): 
  day_quote = TimeStamp.objects.filter(timestamp__date=date)
  day_data = []
  # Check for data. First entry for a new day must be of type START (true)
  if day_quote and day_quote[0].state == False:
    print("Error")
    return [{'start': 0, 'end': 0, 'dur': 0}], 0
  else:
    total = timedelta(0,0,0)
    for index in range(0,len(day_quote),2):
      try:
        start = day_quote[index].timestamp
        end = day_quote[index+1].timestamp
        dur = end-start
        total = total + dur
        day_data.append({'start': start, 'end': end, 'dur': ':'.join(str(dur).split(':')[:2])})
      except:
        pass
    return day_data, total


def check_for_date_crossing(latest):
  today_date = datetime.now().date()
  # Check if current date is different from latest entry date
  if today_date != latest.timestamp.date() and latest.state == True:
    # If latest date was yesterday insert entries on both sides at midnight
    print("Latest entry yesterday")
    if today_date == latest.timestamp.date() + timedelta(1):
      print("Inserting entries at midnight")
      timestamp1 = TimeStamp()
      year = latest.timestamp.date().year
      month = latest.timestamp.date().month
      day = latest.timestamp.date().day
      timestamp1.timestamp = datetime(year,month,day,23,59,59,123456)
      timestamp1.state = False
      timestamp1.save()

      timestamp2 = TimeStamp()
      year = today_date.year
      month = today_date.month
      day = today_date.day
      timestamp2.timestamp = datetime(year,month,day,00,00,00,123456)
      timestamp2.state = True
      timestamp2.save()
    else:
      print("Date entry error")
      if latest.state == True:
        print("Deleting stray entry  - remember to manually input missing hours")


def index(request):
  today_date = datetime.now().date()
  try:
    latest = TimeStamp.objects.latest('id')
    check_for_date_crossing(latest)
    day_data, day_total = get_day_data(today_date)
    context = {'latest': latest, 'today_date': today_date, 'day_data': day_data, 'day_total': ':'.join(str(day_total).split(':')[:2])}
  except:
    context = {'latest': nan, 'today_date': today_date, 'day_data': [], 'day_total': '0:00'}
  return render(request, 'index.html', context)


def new_timestamp(request):
  timestamp = TimeStamp()
  try:
    latest = TimeStamp.objects.latest('id')
    check_for_date_crossing(latest)
    if latest.state == False:
      timestamp.state = True
  except:
    print("No entries")
    timestamp.state = True
  timestamp.save()
  return redirect('/')


def custom_timestamp(request):
  latest = TimeStamp.objects.latest('id')
  current_time =  datetime.now().time()
  timestamp = TimeStamp()
  if latest.state == False:
    timestamp.state = True
  return redirect('/')

