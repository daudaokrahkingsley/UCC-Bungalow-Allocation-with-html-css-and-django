from django.contrib import admin
from .models import Appointment,status_point,Preference

# Register your models here.
admin.site.register(Appointment)
admin.site.register(status_point)
admin.site.register(Preference)