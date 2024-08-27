from django.shortcuts import render,redirect
from .models import Appointment,status_point,Preference,Building,assign_point_and_preference,senior_staff_appointment,designation_point,Preference_senior_staff
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
        present_accommodation = request.POST.get('present_accomodation',None)
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



#senior staff appointment and calculation
#senior staff calculation functions
def calculate_service_points_seniorstaff(dateOf_Uni_Appointment):
    try:
        appointment_date = datetime.strptime(dateOf_Uni_Appointment, '%Y-%m-%d')
        current_date = datetime.now()
        years_of_service = (current_date.year - appointment_date.year)

        # 2 points for each year of service
        service_points = years_of_service * 2
        return service_points

    except ValueError:
        raise ValueError('Invalid date format. Please use YYYY-MM-DD.')

def calculate_present_accommodation_points_seniorstaff(present_accommodation, date_of_occupation_of_accommodation):
    try:
        if not present_accommodation or not date_of_occupation_of_accommodation:
            return 0  # Return 0 if any field is missing
        
        occupation_date = datetime.strptime(date_of_occupation_of_accommodation, '%Y-%m-%d')
        current_date = datetime.now()
        total_months_of_stay = (current_date.year - occupation_date.year) * 12 + abs(current_date.month - occupation_date.month) + 1

        if present_accommodation == 'Senior staff university accommodation':
            # 2 points for every 3 months of stay
            return (total_months_of_stay // 3) * 2
        elif present_accommodation == 'Junior Staff Accommodation' or present_accommodation == 'Not Accommodated':
            # 1 point for each month of stay
            return total_months_of_stay
        else:
            return 0  # No points for other types of accommodation

    except ValueError:
        raise ValueError('Invalid date format. Please use YYYY-MM-DD.')

def cal_marital_points_seniorstaff(marital_status, num_of_children):

    total_point = 0
        
    if marital_status == 'married':
        total_point += 2
        
    if num_of_children:
        total_for_children = num_of_children * 1
        if total_for_children<=5:
            total_point+=total_for_children
        else:
            total_point+=5
    return total_point


#senior staff appointment form
def senior_staff_app(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        staff_number = request.POST.get('staff_number')
        department = request.POST.get('department')
        mobile_number = request.POST.get('mobile_number')
        uni_appointment = request.POST.get('uni_appointment')
        bungalow_no = request.POST.get('bungalow_no', '')
        present_accommodation = request.POST.get('present_accomodation_date',None)
        designation_points = request.POST.get('status_point')
        marital_status = request.POST.get('marital_status', None)
        num_of_children = request.POST.get('num_of_children', 0)
        present_accommodation_name = request.POST.get('present_accommodation_name')

        try:
            status = designation_point.objects.get(status_name=designation_points)
        except designation_point.DoesNotExist:
            messages.error(request, 'Status does not exist')
            return render(request, 'senior_staff_form.html')

        if senior_staff_appointment.objects.filter(staff_number=staff_number).exists():
            messages.error(request, 'Staff number already used in application')
            return render(request, 'senior_staff_form.html')
        user = senior_staff_appointment(
            name=name,
            staff_number=staff_number,
            department=department,
            mobile_no=mobile_number,
            dateOf_Uni_Appointment=uni_appointment,
            designation_point=status.point,
            marital_status=marital_status,
            num_of_children=num_of_children,
        )
        if present_accommodation:
            user.date_of_occupation_ofAccomodation = present_accommodation
        if bungalow_no:
            user.presentUni_bungalow = bungalow_no
        if present_accommodation_name:
            user.present_accommodation = present_accommodation_name
        user.save() 
        staff_number = request.POST.get('staff_number')
        preference_count = int(request.POST.get('preference_count', 0))

        print(f"Staff Number: {staff_number}")
        print(f"Preference Count: {preference_count}")

        try:
            appointment = senior_staff_appointment.objects.get(staff_number=staff_number)
        except senior_staff_appointment.DoesNotExist:
            print("Appointment not found")
            return render(request, 'index.html', {'error': 'Appointment not found'})

        # Clear previous preferences for the same appointment
        Preference_senior_staff.objects.filter(application=appointment).delete()

        # Save preferences
        preferences_saved = 0
        for i in range(preference_count):
            preference_text = request.POST.get(f'preference_{i}')
            print(f"Preference {i}: {preference_text}")  # Debugging output
            if preference_text:
                Preference_senior_staff.objects.create(application=senior_staff_appointment, preference=preference_text)
                preferences_saved += 1
        
        print(f"Total Preferences Saved: {preferences_saved}")

        # Redirect or render success page
        return redirect('senior_staff_form')
    return render(request,'senior_staff_form.html')

#calculate points and assigned preferences based on points
def check_point(request):
    points = None
    marital_point = None
    accommodation_points = 0  # Initialize as 0
    total = 0

    all_appointments = list(Appointment.objects.all())
    all_senior_staff_appointments = list(senior_staff_appointment.objects.all())

    results = []

    # Calculate points for all appointments
    all_appointments_with_points = []

    # Process senior staff appointments first
    for staff_appointment in all_senior_staff_appointments:
        try:
            points = calculate_service_points_seniorstaff(
                staff_appointment.dateOf_Uni_Appointment.strftime('%Y-%m-%d')
            )
            marital_point = cal_marital_points_seniorstaff(
                staff_appointment.marital_status,
                staff_appointment.num_of_children
            )
            if staff_appointment.present_accommodation:  # Only calculate if present_accommodation is not None
                accommodation_points = calculate_present_accommodation_points_seniorstaff(
                    staff_appointment.present_accommodation,
                    staff_appointment.date_of_occupation_ofAccomodation.strftime('%Y-%m-%d') if staff_appointment.date_of_occupation_ofAccomodation else None
                )
                total = int(points) + int(marital_point) + int(accommodation_points)
            else:
                total = int(points) + int(marital_point)

            # Update the senior staff appointment with calculated total points
            staff_appointment.total_points = total
            staff_appointment.save()
             # Determine the category of the staff
            if appointment.staff_number.startswith('sm'):
                category = 'senior_member'
            elif appointment.staff_number.startswith('ss'):
                category = 'senior_staff'
            elif appointment.staff_number.startswith('js'):
                category = 'junior_staff'
            else:
                category = 'unknown'
            # Collect results
            all_appointments_with_points.append({
                'appointment': staff_appointment,
                'total_points': total,
                'category': category
            })

        except senior_staff_appointment.DoesNotExist:
            messages.error(request, 'Error in processing senior staff appointment.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    # Process general appointments
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
                accommodation_points = calculate_accommodation_points(
                    appointment.present_accommodation,
                    appointment.date_of_occupation_ofAccomodation.strftime('%Y-%m-%d') if appointment.date_of_occupation_ofAccomodation else None
                )
                total = int(points) + int(marital_point) + int(accommodation_points)
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

            # Collect results
            all_appointments_with_points.append({
                'appointment': appointment,
                'total_points': total,
                'category': category
            })

        except Appointment.DoesNotExist:
            messages.error(request, 'Error in processing appointment.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    # Sort appointments by total points in descending order
    all_appointments_with_points.sort(key=lambda x: x['total_points'], reverse=True)

    # Assign buildings based on sorted list
    for entry in all_appointments_with_points:
        appointment = entry['appointment']
        total_points = entry['total_points']
        category = entry['category']

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
                        senior_staff = senior_staff_appointment.objects.filter(
                            # No direct query on assigned_building; this is handled in logic
                        )
                        if not senior_staff or all(total_points > s.total_points for s in senior_staff):
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

        # Save the results into the assign_point_and_preference model
        assign_preference, created = assign_point_and_preference.objects.get_or_create(
            application=appointment,
            defaults={'preference_assigned': assigned_building if assigned_building else 'Not Assigned', 'total_points': total_points}
        )
        if not created:
            assign_preference.preference_assigned = assigned_building if assigned_building else 'Not Assigned'
            assign_preference.total_points = total_points
            assign_preference.save()

        # Add to results list for HTML rendering
        results.append({
            'name': appointment.name,
            'staff_number': appointment.staff_number,
            'total_points': total_points,
            'assigned_building': assigned_building if assigned_building else 'Not Assigned'
        })

    return render(request, 'check_point.html', {'results': results})