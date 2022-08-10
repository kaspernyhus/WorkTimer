from django.db import models
from django.utils import timezone

class TimeStamp(models.Model):
  timestamp = models.DateTimeField(default=timezone.now)
  state = models.BooleanField(default=False)
