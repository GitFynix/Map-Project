from django.contrib import admin
from mapnet.models import Location
from mapnet.models import Emailotp
# Register your models here.
# 

admin.site.register(Location) 
admin.site.register(Emailotp)

# from mapnet.views import login 