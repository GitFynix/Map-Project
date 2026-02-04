from django.db import models
from django.utils import timezone

class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)

  

class Emailotp(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)  #ich habe hier Charfield benutzt, weil OTPs manchmal führende Nullen haben können
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    