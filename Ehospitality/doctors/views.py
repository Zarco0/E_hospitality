from django.shortcuts import render, get_object_or_404, redirect
from patients .models import Appointment
from django.contrib.auth.decorators import login_required
from .forms import DoctorProfileForm
from django.core.exceptions import PermissionDenied
from .models import Prescription
from django.db.models import Q
from patients.models import MedicalHistory
from accounts.models import CustomUser
from patients .models import CustomUser, Diagnosis, Medication, Allergy, Treatment, MedicalHistory




@login_required
def manage_profile(request):
    user = request.user

    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('doctors:manage_profile')
    else:
        form = DoctorProfileForm(instance=user)

    return render(request, 'doctors/manage_profile.html', {'form': form, 'user': user})

@login_required
def appointment_schedule(request):
    # Get appointments for the logged-in doctor
    doctor = request.user
    appointments = Appointment.objects.filter(doctor=doctor, status__in=['pending', 'confirmed'])

    return render(request, 'doctors/appointment_schedule.html', {'appointments': appointments})

@login_required
def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.method == 'POST':
        new_date = request.POST['new_date']
        appointment.reschedule(new_date)
        return redirect('doctors:appointment_schedule')
    
    return render(request, 'doctors/reschedule_appointment.html', {'appointment': appointment})

@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.cancel()
    return redirect('doctors:appointment_schedule')

@login_required
def view_appointment(request, id):
    # Fetch the appointment by its ID
    appointment = get_object_or_404(Appointment, id=id)

    # Ensure that only the doctor who owns the appointment can view it (you can modify this logic as per your requirements)
    if request.user != appointment.doctor and not request.user.is_admin:
        raise PermissionDenied

    # Return the appointment details to the template
    return render(request, 'appointments/view_appointment.html', {'appointment': appointment})




@login_required
def doctor_appointments(request):
    if not request.user.is_doctor():
        raise PermissionDenied

    # Get appointments for the logged-in doctor
    appointments = Appointment.objects.filter(doctor=request.user, status='confirmed').order_by('date')

    # Search patients by username or name
    search_query = request.GET.get('search', '')
    if search_query:
        appointments = appointments.filter(
            Q(patient__username__icontains=search_query) |
            Q(patient__email__icontains=search_query)
        )

    return render(request, 'doctors/doctor_appointments.html', {'appointments': appointments})


@login_required
def prescribe_medicine(request, appointment_id):
    if not request.user.is_doctor():
        raise PermissionDenied

    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)

    if request.method == "POST":
        medications = request.POST.get('medications')
        instructions = request.POST.get('instructions')

        # Save the prescription
        Prescription.objects.create(
            appointment=appointment,
            doctor=request.user,
            patient=appointment.patient,
            medications=medications,
            instructions=instructions,
        )

        # Mark the appointment as completed
        appointment.status = 'completed'
        appointment.save()

        return redirect('doctors:doctor_appointments')

    return render(request, 'doctors/prescribe_medicine.html', {'appointment': appointment})

@login_required
def patient_medical_history(request, patient_id):
    if not request.user.is_doctor():
        raise PermissionDenied

    # Get the patient object
    patient = get_object_or_404(CustomUser, id=patient_id, role='Patient')

    # Get the medical history associated with the patient
    medical_history = MedicalHistory.objects.filter(patient=patient).first()

    # If no history is found, create an empty one (optional)
    if not medical_history:
        medical_history = MedicalHistory(patient=patient)
        medical_history.save()

    return render(request, 'doctors/patient_medical_history.html', {
        'patient': patient,
        'medical_history': medical_history,
    })


@login_required
def add_medical_history(request, patient_id):
    patient = CustomUser.objects.get(id=patient_id)
    medical_history, created = MedicalHistory.objects.get_or_create(patient=patient)

    if request.method == 'POST':
        # Handle Diagnosis
        if 'diagnosis_name' in request.POST:
            diagnosis_name = request.POST.get('diagnosis_name')
            date = request.POST.get('diagnosis_date')
            diagnosis = Diagnosis(name=diagnosis_name, date=date)
            diagnosis.save()
            medical_history.diagnoses.add(diagnosis)

        # Handle Medication
        if 'medication_name' in request.POST:
            medication_name = request.POST.get('medication_name')
            dosage = request.POST.get('medication_dosage')
            medication = Medication(name=medication_name, dosage=dosage)
            medication.save()
            medical_history.medications.add(medication)

        # Handle Allergy
        if 'allergy_name' in request.POST:
            allergy_name = request.POST.get('allergy_name')
            severity = request.POST.get('allergy_severity')
            allergy = Allergy(name=allergy_name, severity=severity)
            allergy.save()
            medical_history.allergies.add(allergy)

        # Handle Treatment
        if 'treatment_name' in request.POST:
            treatment_name = request.POST.get('treatment_name')
            date = request.POST.get('treatment_date')
            result = request.POST.get('treatment_result')
            treatment = Treatment(name=treatment_name, date=date, result=result)
            treatment.save()
            medical_history.treatments.add(treatment)

        # Save the medical history
        medical_history.save()

        # Redirect after saving
        return redirect('doctors:patient_medical_history', patient_id=patient.id)

    return render(request, 'doctors/add_medical_history.html', {'patient': patient})

def prescription_history(request, patient_id):
    patient = CustomUser.objects.get(id=patient_id)
    prescriptions = Prescription.objects.filter(patient=patient)
    return render(request, 'doctors/prescription_history.html', {'prescriptions': prescriptions, 'patient': patient})