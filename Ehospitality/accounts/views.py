from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .forms import PatientRegistrationForm
from .models import CustomUser
from patients .models import  Appointment
from django.utils import timezone




def patient_register(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST, request.FILES)
        
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        # Password confirmation check in the view
        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('accounts:register')  # Redirect to registration page
        
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(password)  # Set the password securely
            user.role = 'Patient'  # Default role for patient registration
            user.save()
            
            messages.success(request, "Registration successful! Please log in.")
            return redirect('accounts:login')  # Redirect to login page after successful registration
    else:
        form = PatientRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


# User Login View
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_blocked:  # Check if the user is blocked
                messages.error(request, 'Your account has been blocked. Please contact the admin.')
                return redirect('accounts:login')
            
            login(request, user)
            
            # Redirect user based on role
            if user.is_patient():
                return redirect('accounts:patient_dashboard')  # Redirect to Patient Dashboard
            elif user.is_admin():
                return redirect('accounts:admin_dashboard')  # Redirect to Admin Dashboard
            elif user.is_doctor():
                return redirect('accounts:doctor_dashboard')  # Redirect to Doctor Dashboard
            else:
                messages.error(request, 'Role-based redirection failed.')
                return redirect('accounts:login')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')




# User Logout View
def user_logout(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('accounts:login')


# Dynamic User Dashboard
@login_required
def user_dashboard(request):
    if request.user.is_patient():
        return render(request, 'accounts/patient_dashboard.html')
    elif request.user.is_admin():
        return render(request, 'accounts/admin_dashboard.html')
    elif request.user.is_doctor():
        return render(request, 'accounts/doctor_dashboard.html')
    raise PermissionDenied

# Facility Management View (Admin Feature)
@login_required
def facility_management(request):
    if not request.user.is_admin():
        raise PermissionDenied
    # Logic to manage healthcare facilities
    return render(request, 'admins/facility_management.html')

# Patient Dashboard
@login_required
def patient_dashboard(request):
    if not request.user.is_patient():
        raise PermissionDenied
    # Get appointments for the logged-in user
    appointments = Appointment.objects.filter(patient=request.user)
    
    return render(request, 'accounts/patient_dashboard.html', {'appointments': appointments})


# Admin Dashboard
@login_required

def admin_dashboard(request):
    # Fetch the latest records from the CustomUser, Facility, and Appointment models
    recent_users = CustomUser.objects.all().order_by('-date_joined')[:5]  # Get the 5 most recent users
    recent_appointments = Appointment.objects.all().order_by('-date')[:5]  # Get the 5 most recent appointments

    # Platform Usage Stats (dynamic content)
    active_users = CustomUser.objects.filter(is_blocked=False).count()  # Active users (not blocked)
    total_appointments = Appointment.objects.count()  # Total number of appointments

    # Combine these into a dictionary to pass to the template
    context = {
        'recent_users': recent_users,
        'recent_appointments': recent_appointments,
        'active_users': active_users,
        'total_appointments': total_appointments,
    }

    return render(request, 'accounts/admin_dashboard.html', context)


# Doctor Dashboard
@login_required
def doctor_dashboard(request):
    # Get the current logged-in doctor
    doctor = request.user

    # Filter upcoming appointments for the doctor
    upcoming_appointments = Appointment.objects.filter(
        doctor=doctor,
        date__gte=timezone.now(),  # Only upcoming appointments
        status='confirmed'
    ).order_by('date')

    context = {
        'upcoming_appointments': upcoming_appointments
    }
    return render(request, 'accounts/doctor_dashboard.html', context)

