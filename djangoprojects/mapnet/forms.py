from django import forms
from .models import Location

class RegisterForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ["name", "email", "password"]