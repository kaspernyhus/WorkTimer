from cmath import nan
from time import time
from django.shortcuts import render, redirect
from .models import *
from .forms import ManualEntry
from datetime import datetime, timedelta

from django.utils.formats import date_format
from django.utils import translation
from datetime import date


def format_timedelta(time):
  total_seconds =  time.total_seconds()
  return '%d:%02d' % (total_seconds / 3600, total_seconds / 60 % 60)


def format_total_seconds(total_seconds):
  if total_seconds < 0:
    total_seconds = abs(total_seconds)
    return '-%d:%02d' % (total_seconds / 3600, total_seconds / 60 % 60)
  else:
    return '%d:%02d' % (total_seconds / 3600, total_seconds / 60 % 60)


def get_day_name(day):
  if day == 'Monday':
    return 'Mandag'
  elif day ==  'Tuesday':
    return 'Tirsdag'
  elif day ==  'Wednesday':
    return 'Onsdag'
  elif day ==  'Thursday':
    return 'Torsdag'
  elif day ==  'Friday':
    return 'Fredag'
  elif day ==  'Saturday':
    return 'Lørdag'
  elif day ==  'Sunday':
    return 'Søndag'
  else:
    print("ERROR: weekname not found")
    return ""


def get_quote_info(quote):
  day_data = []
  total = timedelta(0,0,0)
  # No data in quote
  if not quote:
    return [{'ids': (0, 0), 'start': 0, 'end': 0, 'dur': '0:00'}], timedelta(0,0,0)
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
      day_data.append({'ids': ids, 'start': start, 'end': end, 'dur': ':'.join(str(dur).split(':')[:2]), "day_name": get_day_name(start.strftime("%A"))})
    except Exception as e:
      print("!!!! Error getting interval data !!!!", e)
  return day_data, total


def get_day_data(date): 
  day_quote = TimeStamp.objects.filter(timestamp__date=date)
  return get_quote_info(day_quote)


def get_week_data(week_number):
  week_quary = TimeStamp.objects.filter(timestamp__week=week_number)
  week_data, week_total = get_quote_info(week_quary)
  days = []
  for day in week_data:
    try:
      if day['start'].date() not in days:
        days.append(day['start'].date())
    except AttributeError:
      pass
  days.reverse()
  days_data = []
  for day in days:
    day_data, day_total = get_day_data(day)
    days_data.append({'day_data': day_data, 'day_total': format_timedelta(day_total)})
  return days_data, week_total


def get_all_week_numbers():
  this_year = datetime.now().date().year
  all_data = TimeStamp.objects.filter(timestamp__year=this_year)
  weeks = []
  for data in all_data:
    week_number = data.timestamp.date().isocalendar().week
    if week_number not in weeks:
      weeks.append(week_number)
  return weeks, this_year


def get_all_days():
  this_year = datetime.now().date().year
  all_data = TimeStamp.objects.filter(timestamp__year=this_year)
  days = []
  for data in all_data:
    date = data.timestamp.date()
    if date not in days:
      days.append(date)
  days.reverse()
  return days, this_year


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
  now = datetime.now()
  today_date = datetime.now().date()
  week_number = today_date.isocalendar().week
  try:
    latest = TimeStamp.objects.latest('id')
    check_for_date_crossing(latest)
    dur = now - latest.timestamp
  except:
    latest = 0
    dur = '0:00'
  day_data, day_total = get_day_data(today_date)
  week_data, week_total = get_week_data(week_number)
  week_diff = get_week_diff(week_total)
  context = {
    'latest': latest,
    'dur': format_timedelta(dur),
    'today_date': today_date, 
    'week_number': week_number, 
    'week_total': format_timedelta(week_total),
    'day_data': day_data, 
    'day_total': format_timedelta(day_total),
    'week_diff': format_total_seconds(week_diff),
    'acc_margin': get_accumulated_margin()
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
    'day_total': format_timedelta(day_total)}
  return render(request, 'edit_day.html', context)


def edit_all_days(request):
  days, this_year = get_all_days()
  days_data = []
  for day in days:
    day_data, day_total = get_day_data(day)
    days_data.append({'day_data': day_data, 'day_total': format_timedelta(day_total)})
  context = {
    'days_data': days_data, 
    'this_year': this_year }
  return render(request, 'edit_all_days.html', context)


def delete_entry_pair(request, ids):
  redirect_to = request.META.get('HTTP_REFERER')
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
  return redirect(redirect_to)


def edit_entry(request, id):
  if request.method == "POST":
    redirect_to = request.GET.get('next', '/edit_day')
    form = ManualEntry(request.POST)
    if form.is_valid():
      form_data = form.cleaned_data
      entry = TimeStamp.objects.get(id=id)
      entry.timestamp = form_data['timestamp']
      entry.save()
      return redirect(redirect_to)
  entry = TimeStamp.objects.get(id=id)
  form = ManualEntry(initial={'timestamp': entry.timestamp})
  context = {'form': form}
  return render(request, 'manual_timestamp.html', context)


def show_week(request, week_number):
  # today_date = datetime.now().date()
  # week_number = today_date.isocalendar().week
  days_data, week_total = get_week_data(week_number)
  context = {
    'week_number': week_number,
    'days_data': days_data,
    'week_total': format_timedelta(week_total)}
  return render(request, 'week_view.html', context)


def get_week_diff(week_total):
  return week_total.total_seconds() - timedelta(0,0,0,0,0,15).total_seconds()


def show_all_weeks(request):
  week_numbers, this_year = get_all_week_numbers()
  all_week_totals = []
  accumulated_margin = 0
  for week_number in week_numbers:
    days_data, week_total = get_week_data(week_number)
    week_diff = get_week_diff(week_total)
    accumulated_margin += week_diff
    all_week_totals.append({
        'week_number': week_number, 
        'week_total': format_timedelta(week_total), 
        'week_diff': format_total_seconds(week_diff), 
        'accumulated_margin': format_total_seconds(accumulated_margin)
        })
  context = {
    'year': this_year,
    'week_data': all_week_totals}
  return render(request, 'all_weeks_view.html', context)


def get_accumulated_margin():
  week_numbers, this_year = get_all_week_numbers()
  this_week = datetime.now().date().isocalendar().week
  all_week_totals = []
  accumulated_margin = 0
  for week_number in week_numbers:
    days_data, week_total = get_week_data(week_number)
    week_margin = week_total.total_seconds() - timedelta(0,0,0,0,0,15).total_seconds()
    if week_number != this_week:
      accumulated_margin += week_margin
    else:  # only include this weeks hours if more than the 15 hours
      if week_total.total_seconds() > timedelta(0,0,0,0,0,15).total_seconds():
        accumulated_margin += week_margin
  return format_total_seconds(accumulated_margin)
