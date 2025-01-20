from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import HealthResourceForm
from .models import HealthResource
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from patients .models import Appointment
from accounts .models import CustomUser
from django.contrib import messages
from .models import Location, Department, Resource
from .forms import LocationForm, DepartmentForm, ResourceForm
from django.utils import timezone




# Assign Role to a User
@login_required
def assign_role(request, user_id, role):
    if not request.user.is_admin():
        raise PermissionDenied
    user = get_object_or_404(CustomUser, id=user_id)
    if user.role == role:
        messages.warning(request, f"User is already assigned the role: {role}.")
    else:
        user.role = role
        user.save()
        messages.success(request, f"Role assigned successfully: {role}.")
    return redirect('admins:list_users')


# List All Users
@login_required
def list_users(request):
    if not request.user.is_superuser and not request.user.is_admin():
        raise PermissionDenied
    users = CustomUser.objects.all()
    return render(request, 'admins/list_users.html', {'users': users})

@login_required
def block_user(request, user_id):
    if not request.user.is_admin():
        raise PermissionDenied
    user = get_object_or_404(CustomUser, id=user_id)
    if user.is_blocked:
        messages.info(request, f"User {user.username} is already blocked.")
    else:
        user.is_blocked = True
        user.save()
        messages.success(request, f"User {user.username} has been blocked.")
    return redirect('admins:list_users')

@login_required
def unblock_user(request, user_id):
    if not request.user.is_admin():
        raise PermissionDenied
    user = get_object_or_404(CustomUser, id=user_id)
    if not user.is_blocked:
        messages.info(request, f"User {user.username} is already active.")
    else:
        user.is_blocked = False
        user.save()
        messages.success(request, f"User {user.username} has been unblocked.")
    return redirect('admins:list_users')





# Admin: View and manage health resources
@login_required
def manage_health_resources(request):
    if request.user.role != 'Admin':
        return HttpResponseForbidden("Access Denied")
    
    resources = HealthResource.objects.all()
    return render(request, 'adminS/manage_resources.html', {'resources': resources})

# Admin: Add a new resource
@login_required
def add_health_resource(request):
    if request.user.role != 'Admin':
        return HttpResponseForbidden("Access Denied")

    if request.method == 'POST':
        form = HealthResourceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admins:manage_resources')
    else:
        form = HealthResourceForm()
    return render(request, 'admins/add_resource.html', {'form': form})

# Admin: Delete a resource
@login_required
def delete_health_resource(request, resource_id):
    if request.user.role != 'Admin':
        return HttpResponseForbidden("Access Denied")
    
    resource = get_object_or_404(HealthResource, id=resource_id)
    resource.delete()
    return redirect('admins:manage_resources')


@login_required
def appointment_management(request):
    # Check if the user is either an admin or a doctor
    if not (request.user.is_admin or request.user.is_doctor()):
        raise PermissionDenied
    
    # If the user is a doctor, show only the appointments they are involved in
    if request.user.is_doctor():
        appointments = Appointment.objects.filter(doctor=request.user)
    else:
        # Admins can see all appointments
        appointments = Appointment.objects.all()

    context = {
        'appointments': appointments
    }

    return render(request, 'admins/appointment_management.html', context)


def manage_locations(request):
    locations = Location.objects.all()
    return render(request, 'admins/manage_locations.html', {'locations': locations})

def add_location(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admins:manage_locations')
    else:
        form = LocationForm()
    return render(request, 'admins/add_location.html', {'form': form})

# Departments
def manage_departments(request):
    departments = Department.objects.select_related('location').all()
    return render(request, 'admins/manage_departments.html', {'departments': departments})

def add_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admins:manage_departments')
    else:
        form = DepartmentForm()
    return render(request, 'admins/add_department.html', {'form': form})

# Resources
def manage_resources(request):
    resources = Resource.objects.select_related('department__location').all()
    return render(request, 'admins/manage_resources.html', {'resources': resources})

def add_resource(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admins:manage_resources')
    else:
        form = ResourceForm()
    return render(request, 'admins/add_resource.html', {'form': form})

@login_required
def appointment_list(request):
    appointments = Appointment.objects.all()  # You can filter by status or doctor if needed
    return render(request, 'admins/appointments_list.html', {'appointments': appointments})

@login_required
def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, 'admins/appointment_detail.html', {'appointment': appointment})

@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.cancel()  # This will update the status to 'canceled'
    return redirect('admins:appointments_list')  # Redirect back to the appointments list

@login_required
def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        new_date = request.POST.get('new_date')
        # Validate the new date and ensure it's in the future
        if new_date < timezone.now():
            messages.error(request, "You can only reschedule to a future date.")
        else:
            appointment.reschedule(new_date)
            messages.success(request, "Appointment rescheduled successfully!")
            return redirect('admins:appointments_list')
    
    return render(request, 'admins/reschedule_appointment.html', {'appointment': appointment})