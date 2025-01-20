from django.shortcuts import render, redirect, get_object_or_404
from .models import *

from .forms import AppointmentForm
from django.contrib import messages

from django.contrib.auth.decorators import login_required

from datetime import timedelta,datetime
from django.utils.timezone import now

from admins.models import *
from django.http import HttpResponseForbidden

import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY
from django.utils import timezone
from django.core.paginator import Paginator

from django.urls import reverse
from django.http import JsonResponse







# Create your views here.

@login_required
def appointments(request):
    # Retrieve all appointments for the logged-in patient
    appointments = Appointment.objects.filter(patient=request.user)
    return render(request, 'patients/appointments_list.html', {'appointments': appointments})



def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user  # Assign the logged-in user as the patient

            # Assign a fixed appointment fee
            appointment.appointment_fee = 100.00  # Example fixed fee

            appointment.save()
            messages.success(request, "Appointment booked successfully!")
            return redirect('accounts:patient_dashboard')
    else:
        form = AppointmentForm()

    # Get list of doctors
    doctors = CustomUser.objects.filter(role='Doctor')  # Assuming the role for doctors is 'Doctor'

    return render(request, 'patients/appointments.html', {'form': form, 'doctors': doctors,'appointment_fee': 100.00})


# Cancel Appointment
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    appointment.cancel()
    messages.success(request, f"Appointment with {appointment.doctor.username} has been canceled.")
    return redirect('accounts:patient_dashboard')



def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)

    # Ensure timezone-aware comparison
    if appointment.date < now() + timedelta(hours=24):
        messages.error(request, "Appointments can only be rescheduled 24 hours in advance.")
        return redirect('patient:appointments')  # Redirect to the appointment list

    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment rescheduled successfully!")
            return redirect('patient:appointments')
    else:
        form = AppointmentForm(instance=appointment)

    # Get list of doctors
    doctors = CustomUser.objects.filter(role='Doctor')  # Assuming the role for doctors is 'Doctor'
    
    return render(request, 'patients/reschedule_appointment.html', {
        'form': form, 
        'doctors': doctors, 
        'appointment': appointment
    })



# View Medical History
@login_required
def medical_history(request):
    # Fetch the patient's medical history
    medical_history = MedicalHistory.objects.prefetch_related(
        'diagnoses', 'medications', 'allergies', 'treatments'
    ).filter(patient=request.user).first()
    
    # Handle the case where no medical history is found
    if not medical_history:
        return render(request, 'patients/medical_history.html', {
            'medical_history': None,
            'error_message': 'No medical history found for your account.'
        })

    return render(request, 'patients/medical_history.html', {
        'medical_history': medical_history
    })

@login_required
def billing(request, appointment_id):
    # Get the appointment and associated billing details
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    billing = get_object_or_404(Billing, appointment=appointment)

    if request.method == 'POST':
        # Handle payment confirmation
        billing.payment_status = 'paid'
        billing.payment_date = now()
        billing.save()
        messages.success(request, "Payment successfully completed!")
        return redirect('patients:billing', appointment_id=appointment.id)

    return render(request, 'patients/billing.html', {
        'billing': billing,
        'appointment': appointment,
    })


@login_required
def make_payment(request, bill_id):
    bill = get_object_or_404(Billing, id=bill_id, patient=request.user)
    if request.method == 'POST':
        payment_amount = float(request.POST['payment_amount'])
        coverage = bill.insurance_coverage
        amount_due_after_coverage = bill.amount_due - coverage
        
        if payment_amount > amount_due_after_coverage:
            messages.error(request, "Payment amount exceeds the balance due after insurance coverage.")
            return redirect('make_payment', bill_id=bill.id)
        
        bill.amount_paid += payment_amount
        if bill.amount_paid >= bill.amount_due:
            bill.paid = True
        bill.save()
        
        messages.success(request, f"Payment of {payment_amount} processed successfully.")
        return redirect('billing')

    return render(request, 'patients/make_payment.html', {'bill': bill})


def view_health_resources(request):
    if request.user.role != 'Patient':
        return HttpResponseForbidden("Access Denied")
    resources = HealthResource.objects.all().order_by('-created_at')
    return render(request, 'patients/view_resources.html', {'resources': resources})

@login_required
def view_facilities(request):
    """
    View all available healthcare facilities, including locations, departments, and resources.
    """
    locations = Location.objects.prefetch_related('departments__resources').all()
    return render(request, 'patients/view_facilities.html', {
        'locations': locations
    })


@login_required
def department_details(request, department_id):
    """
    View details of a specific department, including its resources.
    """
    department = get_object_or_404(Department.objects.prefetch_related('resources'), id=department_id)
    return render(request, 'patients/department_details.html', {
        'department': department
    })


@login_required
def list_billings(request):
    # Fetch all billings for the logged-in patient
    billings = Billing.objects.filter(patient=request.user)

    # Add pagination (10 records per page)
    paginator = Paginator(billings, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'patients/list_billings.html', {'page_obj': page_obj})


@login_required
def create_checkout_session(request, billing_id):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    billing = get_object_or_404(Billing, id=billing_id)

    if billing.payment_status == 'paid':
        return JsonResponse({'error': 'This billing has already been paid.'}, status=400)

    try:
        # Create a Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'unit_amount': int(billing.amount * 100),  # Stripe expects amount in paise
                    'product_data': {
                        'name': f"Appointment #{billing.appointment.id}",
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('patient:payment_success', args=[billing.id])),
            cancel_url=request.build_absolute_uri(reverse('patient:payment_cancel', args=[billing.id])),
        )
        return redirect(checkout_session.url, code=303)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def payment_success(request, billing_id):
    """
    Handles successful payment and updates the Billing and Appointment statuses.
    """
    billing = get_object_or_404(Billing, id=billing_id)

    # Update the payment status and appointment status if payment is pending
    if billing.payment_status == 'pending':
        billing.payment_status = 'paid'
        billing.payment_date = timezone.now()
        billing.save()

        # Mark the appointment as confirmed
        billing.appointment.status = 'confirmed'
        billing.appointment.save()

    return render(request, 'patients/payment_success.html', {'billing': billing})


@login_required
def payment_cancel(request, billing_id):
    """
    Handles canceled payment. No changes to statuses are made.
    """
    billing = get_object_or_404(Billing, id=billing_id)
    return render(request, 'patients/payment_cancel.html', {'billing': billing})