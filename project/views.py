from django.shortcuts import render,redirect
from .models import Appointment,status_point,Preference
from django.contrib import messages
# Create your views here.
from datetime import datetime, timedelta

def calculate_accommodation_points(present_accommodation, present_accommodation_date):
    print(f"Present Accommodation: {present_accommodation}")
    print(f"Present Accommodation Date: {present_accommodation_date}")
    
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


def cal_marital_points(duty_status,marital_status,num_of_children,date_of_duty =None):
    try:

        total_point=0
        months_ = datetime.now()
        duty = datetime.strptime(date_of_duty, '%Y-%m-%d')
        months_of_duty = ((months_.year - duty.year) * 12 ) + (abs(months_.month - duty.month))
        try:
            
            if marital_status == 'married':
                total_point+=2
                
            if num_of_children:
                total_for_children = num_of_children * 1
                if total_for_children<=5:
                    total_point+=total_for_children
                else:
                    total_point+=5
            if duty_status == 'head of department' or 'deans' or 'provert':
                if months_of_duty>=12:
                    total_point+=3
                    print(duty_status)
            else:
                total_point+=0
        except:
            total_point=0
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


def index(request):
    if request.method == 'POST':
        name = request.POST['name']
        staff_number = request.POST['staff_number']
        department = request.POST['department']
        mobile_number = request.POST['mobile_number']
        uni_appointment = request.POST['uni_appointment']
        bungalow_no = request.POST.get('bungalow_no', '')
        present_accomodation = request.POST.get('present_accomodation', None)
        present_accomodation_name = request.POST.get('present_accommodation_name')
        status_points = request.POST['status_point']
        study_leaveFrom = request.POST.get('study_leaveFrom', None)
        study_leaveTo = request.POST.get('study_leaveTo', None)
        marital_status = request.POST.get('marital_status', None)  # Get the single value
        duty_status = request.POST.get('duty_status', None)  # Get the single value
        num_of_children = request.POST['num_of_children']
        date_of_duty = request.POST.get('date_of_duty', None)

        # Validate and handle empty strings
        print(present_accomodation)
        if marital_status:
            print(marital_status)
        else:
            print("No marital status provided")
        
        if duty_status:
            print(duty_status)
        else:
            print("No duty status provided")
        
        try:
            status = status_point.objects.get(status_name=status_points)
        except status_point.DoesNotExist:
            messages.error(request, 'Status does not exist')
            return render(request, 'index.html')

        if Appointment.objects.filter(staff_number=staff_number).exists():
            messages.error(request, 'Staff number already used in application')
            return render(request, 'index.html')

        # Create the Appointment object with mandatory fields
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
       

        # Add optional fields if provided
        if study_leaveFrom:
            user.studyLeave_from = study_leaveFrom
        if study_leaveTo:
            user.studyLeave_to = study_leaveTo
        if date_of_duty:
            user.date_of_duty = date_of_duty
        if present_accomodation:
            user.date_of_occupation_ofAccomodation = present_accomodation
        if present_accomodation_name:
            user.present_accommodation = present_accomodation_name
        if duty_status:
            user.duty_status=duty_status

        try:
            user.save()
             # Create Preference object
            Preference.objects.create(
                application=user,
                preference_a=request.POST.get('preference_a', ''),
                preference_b=request.POST.get('preference_b', ''),
                preference_c=request.POST.get('preference_c', ''),
                preference_d=request.POST.get('preference_d', ''),
                preference_e=request.POST.get('preference_e', ''),
                preference_f=request.POST.get('preference_f', ''),
                preference_g=request.POST.get('preference_g', ''),
                preference_h=request.POST.get('preference_h', ''),
                preference_i=request.POST.get('preference_i', '')
            )
            messages.success(request, 'Data saved successfully')
            return redirect('index')
        except Exception as e:
            messages.error(request, f"Error saving data: {e}")
            return redirect('index')
        
    
    return render(request, 'index.html')






def check_point(request):
    points = None
    marital_point = None
    accomodation_points = None
    total = 0
    if request.method == 'POST':
        staff_number = request.POST.get('staff_number')
        print(f"Staff Number: {staff_number}")
        try:
            appointment = Appointment.objects.get(staff_number=staff_number)
            appoint_id = appointment.id
            print(f"Appointment: {appointment}")
            print(f"Appointmentm: {appointment.marital_status}")
            print(f"Present Accommodation: {appointment.present_accommodation}")

            points = calculate_status_points(
                appointment.initial_point,
                appointment.dateOf_Uni_Appointment.strftime('%Y-%m-%d'),
                appointment.studyLeave_from.strftime('%Y-%m-%d') if appointment.studyLeave_from else None,
                appointment.studyLeave_to.strftime('%Y-%m-%d') if appointment.studyLeave_to else None
            )
            print(f"Status Points: {points}")

            marital_point = cal_marital_points(
                appointment.duty_status,
                appointment.marital_status,
                appointment.num_of_children,
                appointment.date_of_duty.strftime('%Y-%m-%d') if appointment.date_of_duty else None,
            )
            print(f"Marital Points: {marital_point}")

            accomodation_points = calculate_accommodation_points(
                appointment.present_accommodation,
                appointment.date_of_occupation_ofAccomodation.strftime('%Y-%m-%d') if appointment.date_of_occupation_ofAccomodation else None
            )
            print(f"Accommodation Points: {accomodation_points}")

            total = int(points) + int(marital_point) + int(accomodation_points)
            print(f"Total Points: {total}")

        except Appointment.DoesNotExist:
            messages.error(request, 'Staff number not found.')

    return render(request, 'check_point.html', {'point': total})
