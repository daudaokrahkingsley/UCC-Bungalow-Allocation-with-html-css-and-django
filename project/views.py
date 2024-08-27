from django.shortcuts import render,redirect
from .models import Appointment,status_point,Preference,Building,assign_point_and_preference
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from datetime import datetime, timedelta

def admin_manage_buildings(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category')
        vacant_rooms = request.POST.get('vacant_rooms')

        if name and category and vacant_rooms:
            Building.objects.create(
                name=name,
                category=category,
                vacant_rooms=int(vacant_rooms)
            )
            messages.success(request, 'Building added successfully')
            return redirect('manage_buildings')
        else:
            messages.error(request, 'Please provide all required fields')

    buildings = Building.objects.all()
    return render(request, 'admin_manage.html', {'buildings': buildings})


def calculate_accommodation_points(present_accommodation, present_accommodation_date):
    if present_accommodation is None or present_accommodation_date is None:
        return 0  # Skip calculation if either value is None

    present_date = datetime.strptime(present_accommodation_date, '%Y-%m-%d')
    current_date = datetime.now()
    months_of_stay = (current_date.year - present_date.year) * 12 + abs(current_date.month - present_date.month) + 1

    if present_accommodation == 'off_campus':
        return months_of_stay // 3
    elif present_accommodation == 'on_campus':
        return months_of_stay // 6
    elif present_accommodation == 'temporary_accommodation':
        return months_of_stay // 2
    elif present_accommodation == 'not_accommodated':
        return months_of_stay
    else:
        return 0



def cal_marital_points(duty_status, marital_status, num_of_children, date_of_duty=None):
    try:
        total_point = 0
        if date_of_duty:
            months_ = datetime.now()
            duty = datetime.strptime(date_of_duty, '%Y-%m-%d')
            months_of_duty = ((months_.year - duty.year) * 12) + (months_.month - duty.month)
        else:
            months_of_duty = 0  # Set to 0 if date_of_duty is None
        
        if marital_status == 'married':
            total_point += 2
        
        if num_of_children:
                total_for_children = num_of_children * 1
                if total_for_children<=5:
                    total_point+=total_for_children
                else:
                    total_point+=5

        if duty_status in ['head of department', 'deans', 'provert']:
            if months_of_duty >= 12:
                total_point += 3
        
        return total_point

    except ValueError as e:
        print(e)
        raise ValueError('Invalid date format. Please use YYYY-MM-DD.')

def calculate_status_points(initial_point, dateOf_Uni_Appointment, study_leaveFrom=None, study_leaveTo=None):
    try:
        total_points = 0

        # Calculate points based on months in service
        appointment_date = datetime.strptime(dateOf_Uni_Appointment, '%Y-%m-%d')
        current_date = datetime.now()
        months_in_service = (current_date.year - appointment_date.year) * 12 + abs(current_date.month - appointment_date.month)

        # Remove months during the study leave from the service period calculation
        if study_leaveFrom and study_leaveTo:
            leave_from = datetime.strptime(study_leaveFrom, '%Y-%m-%d')
            leave_to = datetime.strptime(study_leaveTo, '%Y-%m-%d')
            leave_months = (leave_to.year - leave_from.year) * 12 + abs(leave_to.month - leave_from.month) + 1
            months_in_service -= leave_months
        
        # Assign 1 point for each month in service
        total_points += months_in_service

        # Calculate study leave points
        if study_leaveFrom and study_leaveTo:
            leave_from = datetime.strptime(study_leaveFrom, '%Y-%m-%d')
            leave_to = datetime.strptime(study_leaveTo, '%Y-%m-%d')
            current_month = leave_from
            
            while current_month <= leave_to:
                consecutive_leave_months = 1
                next_month = current_month + timedelta(days=32)
                next_month = next_month.replace(day=1)

                while next_month <= leave_to:
                    consecutive_leave_months += 1
                    next_month += timedelta(days=32)
                    next_month = next_month.replace(day=1)

                if consecutive_leave_months >= 3:
                    total_points += 1
                
                current_month = next_month
            else:
                total_points+=1
                current_month += timedelta(days=32)

        return total_points + initial_point
    
    except ValueError:
        raise ValueError('Invalid date format. Please use YYYY-MM-DD.')
def delete_building(request, building_id):
    if request.method == 'POST':
        building = get_object_or_404(Building, id=building_id)
        building.delete()
        return redirect(reverse('manage_buildings'))
    return redirect(reverse('manage_buildings'))

def get_buildings(request):
    staff_number = request.GET.get('staff_number')
    category = ''

    # Determine the category based on the staff number prefix
    if staff_number.startswith('sm'):
        category = 'senior_member'
    elif staff_number.startswith('ss'):
        category = 'senior_staff'
    elif staff_number.startswith('js'):
        category = 'junior_staff'

    # Fetch buildings based on the determined category
    available_buildings = Building.objects.filter(category=category, vacant_rooms__gt=0)
    building_names = [building.name for building in available_buildings]

    # Return the building names as a JSON response
    return JsonResponse({'preferences': building_names})

def view_all_preferences(request):
    applications = Appointment.objects.all()
    preferences = Preference.objects.select_related('application').all()

    # Create a dictionary to group preferences by staff number
    preferences_dict = {}
    for pref in preferences:
        staff_number = pref.application.staff_number
        if staff_number not in preferences_dict:
            preferences_dict[staff_number] = {
                'name': pref.application.name,
                'department': pref.application.department,
                'preferences': []
            }
        preferences_dict[staff_number]['preferences'].append(pref.preference)
    
    return render(request, 'view_preferences.html', {
        'applications': applications,
        'preferences_dict': preferences_dict
    })


def index(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        staff_number = request.POST.get('staff_number')
        department = request.POST.get('department')
        mobile_number = request.POST.get('mobile_number')
        uni_appointment = request.POST.get('uni_appointment')
        bungalow_no = request.POST.get('bungalow_no', '')
        present_accommodation = request.POST.get('present_accomodation_date',None)
        present_accommodation_name = request.POST.get('present_accommodation_name')
        status_points = request.POST.get('status_point')
        study_leaveFrom = request.POST.get('study_leaveFrom', None)
        study_leaveTo = request.POST.get('study_leaveTo', None)
        marital_status = request.POST.get('marital_status', None)
        duty_status = request.POST.get('duty_status', None)
        num_of_children = request.POST.get('num_of_children', 0)
        date_of_duty = request.POST.get('date_of_duty', None)
        print(f"Date: {present_accommodation}")

        try:
            status = status_point.objects.get(status_name=status_points)
        except status_point.DoesNotExist:
            messages.error(request, 'Status does not exist')
            return render(request, 'index.html')

        if Appointment.objects.filter(staff_number=staff_number).exists():
            messages.error(request, 'Staff number already used in application')
            return render(request, 'index.html')

        user = Appointment(
            name=name,
            staff_number=staff_number,
            department=department,
            mobile_no=mobile_number,
            dateOf_Uni_Appointment=uni_appointment,
            presentUni_bungalow=bungalow_no,
            initial_point=status.point,
            marital_status=marital_status,
            num_of_children=num_of_children,
        )

        if study_leaveFrom:
            user.studyLeave_from = study_leaveFrom
        if study_leaveTo:
            user.studyLeave_to = study_leaveTo
        if date_of_duty:
            user.date_of_duty = date_of_duty
        if present_accommodation:
            user.date_of_occupation_ofAccomodation = present_accommodation
        if present_accommodation_name:
            user.present_accommodation = present_accommodation_name
        if duty_status:
            user.duty_status = duty_status

        user.save() 
        staff_number = request.POST.get('staff_number')
        preference_count = int(request.POST.get('preference_count', 0))

        print(f"Staff Number: {staff_number}")
        print(f"Preference Count: {preference_count}")

        try:
            appointment = Appointment.objects.get(staff_number=staff_number)
        except Appointment.DoesNotExist:
            print("Appointment not found")
            return render(request, 'index.html', {'error': 'Appointment not found'})

        # Clear previous preferences for the same appointment
        Preference.objects.filter(application=appointment).delete()

        # Save preferences
        preferences_saved = 0
        for i in range(preference_count):
            preference_text = request.POST.get(f'preference_{i}')
            print(f"Preference {i}: {preference_text}")  # Debugging output
            if preference_text:
                Preference.objects.create(application=appointment, preference=preference_text)
                preferences_saved += 1
        
        print(f"Total Preferences Saved: {preferences_saved}")

        # Redirect or render success page
        return redirect('check_point')
    return render(request, 'index.html')



def check_point(request):
    points = None
    marital_point = None
    accomodation_points = 0  # Initialize as 0
    total = 0
    all_appointments = Appointment.objects.all()
    results = []

    for appointment in all_appointments:
        try:
            points = calculate_status_points(
                appointment.initial_point,
                appointment.dateOf_Uni_Appointment.strftime('%Y-%m-%d'),
                appointment.studyLeave_from.strftime('%Y-%m-%d') if appointment.studyLeave_from else None,
                appointment.studyLeave_to.strftime('%Y-%m-%d') if appointment.studyLeave_to else None
            )
            marital_point = cal_marital_points(
                appointment.duty_status,
                appointment.marital_status,
                appointment.num_of_children,
                appointment.date_of_duty.strftime('%Y-%m-%d') if appointment.date_of_duty else None,
            )
            if appointment.present_accommodation:  # Only calculate if present_accommodation is not None
                accomodation_points = calculate_accommodation_points(
                    appointment.present_accommodation,
                    appointment.date_of_occupation_ofAccomodation.strftime('%Y-%m-%d') if appointment.date_of_occupation_ofAccomodation else None
                )
                total = int(points) + int(marital_point) + int(accomodation_points)
            else:
                total = int(points) + int(marital_point)

            # Determine the category of the staff
            if appointment.staff_number.startswith('sm'):
                category = 'senior_member'
            elif appointment.staff_number.startswith('ss'):
                category = 'senior_staff'
            elif appointment.staff_number.startswith('js'):
                category = 'junior_staff'
            else:
                category = 'unknown'

            # Assign a building
            assigned_building = None
            if category == 'senior_member':
                available_buildings = Building.objects.filter(category='senior_member', vacant_rooms__gt=0).order_by('-vacant_rooms')
                for building in available_buildings:
                    if building.vacant_rooms > 0:
                        building.vacant_rooms -= 1
                        building.save()
                        assigned_building = building.name
                        break
                if not assigned_building:
                    available_buildings = Building.objects.filter(category='senior_staff', vacant_rooms__gt=0).order_by('-vacant_rooms')
                    for building in available_buildings:
                        if building.vacant_rooms > 0:
                            senior_staff = Appointment.objects.filter(staff_number__startswith='ss', assigned_building=building.name)
                            if not senior_staff or all(total > s.total_points for s in senior_staff):
                                building.vacant_rooms -= 1
                                building.save()
                                assigned_building = building.name
                                break
                if not assigned_building:
                    available_buildings = Building.objects.filter(category='junior_staff', vacant_rooms__gt=0).order_by('-vacant_rooms')
                    for building in available_buildings:
                        if building.vacant_rooms > 0:
                            building.vacant_rooms -= 1
                            building.save()
                            assigned_building = building.name
                            break
            elif category == 'senior_staff':
                available_buildings = Building.objects.filter(category='senior_staff', vacant_rooms__gt=0).order_by('-vacant_rooms')
                for building in available_buildings:
                    if building.vacant_rooms > 0:
                        building.vacant_rooms -= 1
                        building.save()
                        assigned_building = building.name
                        break
                if not assigned_building:
                    available_buildings = Building.objects.filter(category='junior_staff', vacant_rooms__gt=0).order_by('-vacant_rooms')
                    for building in available_buildings:
                        if building.vacant_rooms > 0:
                            building.vacant_rooms -= 1
                            building.save()
                            assigned_building = building.name
                            break
            elif category == 'junior_staff':
                available_buildings = Building.objects.filter(category='junior_staff', vacant_rooms__gt=0).order_by('-vacant_rooms')
                for building in available_buildings:
                    if building.vacant_rooms > 0:
                        building.vacant_rooms -= 1
                        building.save()
                        assigned_building = building.name
                        break

            # Save the results into the `assign_point_and_preference` model
            assign_preference = assign_point_and_preference.objects.filter(
                application=appointment,
                preference_assigned=assigned_building if assigned_building else 'Not Assigned',
                total_points=total
            )

            # Add to results list for HTML rendering
            results.append({
                'name': appointment.name,
                'staff_number': appointment.staff_number,
                'total_points': total,
                'assigned_building': assigned_building if assigned_building else 'Not Assigned'
            })

        except Appointment.DoesNotExist:
            messages.error(request, 'Error in processing appointment.')
        except assign_point_and_preference.DoesNotExist:
            # Handle case where assignment doesn't exist
            pass

    return render(request, 'check_point.html', {'results': results})
