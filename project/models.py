from django.db import models
from datetime import date  

class Building(models.Model):
    CATEGORY_CHOICES = [
        ('senior_member', 'Senior Member'),
        ('senior_staff', 'Senior Staff'),
        ('junior_staff', 'Junior Staff'),
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    vacant_rooms = models.IntegerField()

    def __str__(self):
        return f"{self.name} ({self.category}) - {self.vacant_rooms} rooms available"

class Appointment(models.Model):
    name = models.CharField(max_length=100)
    staff_number = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    mobile_no = models.IntegerField()
    dateOf_Uni_Appointment = models.DateField(default=date.today)
    presentUni_bungalow = models.CharField(max_length=100)
    date_of_occupation_ofAccomodation = models.DateField(null=True, blank=True)
    studyLeave_from = models.DateField(null=True, blank=True)
    studyLeave_to = models.DateField(null=True, blank=True)
    initial_point = models.IntegerField(default=0)
    marital_status_choices = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('none', 'None')
    ]
    marital_status = models.CharField(max_length=50, choices=marital_status_choices, default='Single')
    duty_status_choices = [
        ('provert', 'Provert'),
        ('deans', 'Deans'),
        ('head of department', 'Head of Department')
    ]
    duty_status = models.CharField(max_length=50, choices=duty_status_choices, default='Provert')
    num_of_children = models.IntegerField()
    date_of_duty = models.DateField(null=True, blank=True)
    
    present_accommodation = models.CharField(max_length=50, choices=[('off_campus', 'Off Campus'), ('on_campus', 'On Campus'), ('temporary_accommodation', 'Temporary Accommodation'), ('not_accommodated', 'Not Accommodated')], default='Not Accomodated')

    def get_category(self):
        if self.staff_number.startswith('sm'):
            return 'senior_member'
        elif self.staff_number.startswith('ss'):
            return 'senior_staff'
        elif self.staff_number.startswith('js'):
            return 'junior_staff'
        return 'unknown'
    
    def __str__(self):
        return self.name

class Preference(models.Model):
    application = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='preference_set')
    preference = models.CharField(max_length=255, default='ff1')

    def __str__(self):
        return f"Preferences for {self.application.name}"

class assign_point_and_preference(models.Model):
    application = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='assigned_point_and_preference_set')
    preference_assigned = models.CharField(max_length=255, null=True, blank=True)
    total_points = models.IntegerField(default=0)

    def __str__(self):
        return f"Assigned point and preference for {self.application.name}"
    
class status_point(models.Model):
    status_name = models.CharField(max_length=100)
    point = models.IntegerField()

    def __str__(self):
        return self.status_name

class senior_staff_appointment(models.Model):
    name = models.CharField(max_length=100)
    staff_number = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    mobile_no = models.IntegerField()
    dateOf_Uni_Appointment = models.DateField(default=date.today)
    presentUni_bungalow = models.CharField(max_length=100)
    date_of_occupation_ofAccomodation = models.DateField(null=True, blank=True)
    designation_point = models.IntegerField(default=0)
    marital_status_choices = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('none', 'None')
    ]
    marital_status = models.CharField(max_length=50, choices=marital_status_choices, default='Single')
    num_of_children = models.IntegerField()
    total_points = models.IntegerField(default=0)
    present_accommodation = models.CharField(max_length=50, choices=[('Senior staff university accommodation', 'Senior staff university accommodation'), ('Junior staff bungalow', 'Junior Staff Bungalow'), ('not_accommodated', 'Not Accommodated')], default='Not Accomodated')

class designation_point(models.Model):
    status_name = models.CharField(max_length=100)
    point = models.IntegerField()

    def __str__(self):
        return self.status_name

class Preference_senior_staff(models.Model):
    application = models.ForeignKey(senior_staff_appointment, on_delete=models.CASCADE, related_name='preference_set')
    preference = models.CharField(max_length=255, default='sn1')

    def __str__(self):
        return f"Preferences for {self.application.name}"

class assign_point_and_preference_senior(models.Model):
    application = models.ForeignKey(senior_staff_appointment, on_delete=models.CASCADE, related_name='assigned_point_and_preference_set')
    preference_assigned = models.CharField(max_length=255, null=True, blank=True)
    total_points = models.IntegerField(default=0)

    def __str__(self):
        return f"Assigned point and preference for {self.application.name}"