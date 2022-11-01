from django.db import models
from django.utils import timezone

class TimeStamp(models.Model):
  timestamp = models.DateTimeField(default=timezone.now)
  state = models.BooleanField(default=False)

class HourlyGoals(models.Model):
  timestamp = models.DateTimeField(default=timezone.now)
  week_number = models.IntegerField(default=1)
  weekly_hours = models.IntegerField(default=20)
