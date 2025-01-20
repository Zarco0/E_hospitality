from .models import *
from django import forms
from django.utils.timezone import now  
from accounts.models import CustomUser



class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'reason']

    def clean_date(self):
        date = self.cleaned_data.get('date')

        if date < now():  # Compare with timezone-aware current datetime
            raise forms.ValidationError("The date cannot be in the past.")
        return date
    
