from django.contrib import admin
from .models import Appointment,status_point,Preference,Building,assign_point_and_preference,senior_staff_appointment,designation_point,Preference_senior_staff,assign_point_and_preference_senior

# Register your models here.
admin.site.register(Appointment)
admin.site.register(status_point)
admin.site.register(Preference)
admin.site.register(Building)
admin.site.register(assign_point_and_preference)
admin.site.register(senior_staff_appointment)
admin.site.register(designation_point)
admin.site.register(Preference_senior_staff)
admin.site.register(assign_point_and_preference_senior)