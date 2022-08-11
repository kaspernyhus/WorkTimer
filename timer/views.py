from cmath import nan
from time import time
from django.shortcuts import render, redirect
from .models import *
from .forms import ManualEntry
from datetime import datetime, timedelta


def format_timedelta(time):
  return ':'.join(str(time).split(':')[:2])


def get_quote_info(quote):
  day_data = []
  total = timedelta(0,0,0)
  # No data in quote
  if not quote:
    return [{'start': 0, 'end': 0, 'dur': 0}], 0
  # Quote must start with state True
  if quote[0].state == False:
    start_index = 1
  else:
    start_index = 0
  for index in range(start_index,len(quote),2):
    try:
      ids = (quote[index].id, quote[index+1].id)
      start = quote[index].timestamp
      end = quote[index+1].timestamp
      dur = end-start
      total = total + dur
      day_data.append({'ids': ids, 'start': start, 'end': end, 'dur': ':'.join(str(dur).split(':')[:2])})
    except Exception as e:
      print("!!!! Error getting interval data !!!!", e)
  return day_data, total


def get_day_data(date): 
  day_quote = TimeStamp.objects.filter(timestamp__date=date)
  return get_quote_info(day_quote)


def get_week_data(week_number):
  week_quary = TimeStamp.objects.filter(timestamp__week=week_number)
  return get_quote_info(week_quary)


def insert_entry(year, month, day, hour, minute, second, state):
  timestamp = TimeStamp()
  timestamp.timestamp = datetime(year,month,day,hour,minute,second)
  timestamp.state = state
  timestamp.save()


def check_for_date_crossing(latest):
  today_date = datetime.now().date()
  # Check if current date is different from latest entry date
  if today_date != latest.timestamp.date() and latest.state == True:
    # If latest date was yesterday insert entries on both sides at midnight
    print("Latest entry yesterday")
    if today_date == latest.timestamp.date() + timedelta(1):
      print("Inserting entries at midnight")
      insert_entry(
        latest.timestamp.date().year,
        latest.timestamp.date().month,
        latest.timestamp.date().day,
        23,59,59,False)
      insert_entry(
        today_date.year,
        today_date.month,
        today_date.day,
        00,00,00,True)
    else:
      print("Date entry error")
      if latest.state == True:
        print("Deleting stray entry  - remember to manually input missing hours")


def index(request):
  today_date = datetime.now().date()
  week_number = today_date.isocalendar().week
  try:
    latest = TimeStamp.objects.latest('id')
    check_for_date_crossing(latest)
  except:
    latest = 0
  day_data, day_total = get_day_data(today_date)
  week_data, week_total = get_week_data(week_number)
  context = {
    'latest': latest, 
    'today_date': today_date, 
    'week_number': week_number, 
    'week_total': format_timedelta(week_total),
    'day_data': day_data, 
    'day_total': format_timedelta(day_total)
  }
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


def manual_timestamp(request):  
  if request.method == "POST":
    form = ManualEntry(request.POST)
    if form.is_valid():
      form_data = form.cleaned_data
      data_to_save = form.save(commit=False)
      try:
        latest = TimeStamp.objects.latest('id')
        check_for_date_crossing(latest)
        if latest.state == False:
          data_to_save.state = True
      except:
        data_to_save.state = False
      data_to_save.save()
      return redirect('/')
  form = ManualEntry()
  context = {'form': form}
  return render(request, 'manual_timestamp.html', context)


def edit_day(request):
  today_date = datetime.now().date()
  day_data, day_total = get_day_data(today_date)
  context = {
    'today_date': today_date, 
    'day_data': day_data, 
    'day_total': format_timedelta(day_total)
  }
  return render(request, 'edit_day.html', context)


def delete_entry_pair(request, ids):
  IDs = eval(ids)
  first_id = IDs[0]
  second_id = IDs[1]
  try:
    time1 = TimeStamp.objects.get(id=first_id)
    time2 = TimeStamp.objects.get(id=second_id)
    time1.delete()
    time2.delete()
    print("Deleted entries")
  except:
    print("Error getting first entry")
  return redirect('/edit_day')


def edit_entry(request, id):
  if request.method == "POST":
    form = ManualEntry(request.POST)
    if form.is_valid():
      form_data = form.cleaned_data
      entry = TimeStamp.objects.get(id=id)
      entry.timestamp = form_data['timestamp']
      entry.save()
      return redirect('/edit_day')

  entry = TimeStamp.objects.get(id=id)
  form = ManualEntry(initial={
    'timestamp': entry.timestamp
  })
  context = {'form': form}
  return render(request, 'manual_timestamp.html', context)


def show_week(request):
  today_date = datetime.now().date()
  week_number = today_date.isocalendar().week
  week_data, week_total = get_week_data(week_number)
  
  context = {
    'today_date': today_date, 
    'week_number': week_number, 
    'week_data': week_data,
    'week_total': format_timedelta(week_total),
  }
  return render(request, 'week_view.html', context)


def get_all_week_numbers():
  this_year = datetime.now().date().year
  all_data = TimeStamp.objects.filter(timestamp__year=this_year)
  weeks = []
  for data in all_data:
    week_number = data.timestamp.date().isocalendar().week
    if week_number not in weeks:
      weeks.append(week_number)
  return weeks, this_year


def show_all_weeks(request):
  week_numbers, this_year = get_all_week_numbers()
  all_week_totals = []
  for week_number in week_numbers:
    week_data, week_total = get_week_data(week_number)
    all_week_totals.append({'week_number': week_number, 'week_total': format_timedelta(week_total)})
  
  context = {
    'year': this_year,
    'week_data': all_week_totals,
  }
  return render(request, 'all_weeks_view.html', context)
