from django import forms
from .models import RegisteredUser

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = RegisteredUser
        fields = ['name', 'roll_no', 'phone', 'year', 'branch', 'section']
