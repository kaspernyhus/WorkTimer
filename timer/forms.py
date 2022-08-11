from django import forms
from .models import TimeStamp


class DateInput(forms.DateInput):
    input_type = 'date'


class ManualEntry(forms.ModelForm):
  class Meta:
      model = TimeStamp
      fields = [
          'timestamp',
      ]
      widgets = {
          'date': DateInput(attrs={'class': 'input'}),
      }
      labels = {
          'timestamp': 'Dato og tidspunkt',
      }