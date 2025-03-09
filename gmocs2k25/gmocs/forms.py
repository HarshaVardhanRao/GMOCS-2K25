from django import forms
from .models import registrations

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = registrations
        fields = ['username', 'roll_no', 'phone', 'year', 'branch', 'section']
