from django.db import models
from datetime import date  

class Appointment(models.Model):
    name = models.CharField(max_length=100)
    staff_number = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    mobile_no = models.IntegerField()
    dateOf_Uni_Appointment = models.DateField(default=date.today)  # Default date object
    presentUni_bungalow = models.CharField(max_length=100)
    date_of_occupation_ofAccomodation = models.DateField(null=True,blank=True)  # Default date object
    studyLeave_from = models.DateField(null=True, blank=True)
    studyLeave_to = models.DateField(null=True, blank=True)
    initial_point = models.IntegerField(default=0)
    marital_status_choices = [
        ('single','Single'),
        ('married','Married'),
        ('none','None')
    ]
    marital_status = models.CharField(max_length=50,choices=marital_status_choices,default='Single')
    duty_status_choices = [
        ('provert','Provert'),
        ('deans','Deans'),
        ('head of department','Head of Department')
    ]
    duty_status = models.CharField(max_length=50,choices=duty_status_choices,default='Provert')
    num_of_children = models.IntegerField()
    date_of_duty = models.DateField(null=True, blank=True)
    present_accommodation = models.CharField(max_length=50, choices=[('off_campus', 'Off Campus'), ('on_campus', 'On Campus'), ('temporary_accommodation', 'Temporary Accommodation'), ('not_accommodated', 'Not Accommodated')],default='Not Accomodated')

    def __str__(self):
        return self.name
class Preference(models.Model):
    application = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='preferences')
    preference_a = models.CharField(max_length=255, blank=True, null=True)
    preference_b = models.CharField(max_length=255, blank=True, null=True)
    preference_c = models.CharField(max_length=255, blank=True, null=True)
    preference_d = models.CharField(max_length=255, blank=True, null=True)
    preference_e = models.CharField(max_length=255, blank=True, null=True)
    preference_f = models.CharField(max_length=255, blank=True, null=True)
    preference_g = models.CharField(max_length=255, blank=True, null=True)
    preference_h = models.CharField(max_length=255, blank=True, null=True)
    preference_i = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Preferences for {self.application.name}"
    

class status_point(models.Model):
    status_name = models.CharField(max_length=100)
    point = models.IntegerField()

    def __str__(self):
        return self.status_name
