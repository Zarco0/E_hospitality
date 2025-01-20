from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('profile/', views.manage_profile, name='manage_profile'),
    path('appointments/', views.appointment_schedule, name='appointment_schedule'),
    path('appointments/reschedule/<int:appointment_id>/', views.reschedule_appointment, name='reschedule_appointment'),
    path('appointments/cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('docappointments/', views.doctor_appointments, name='doctor_appointments'),
    path('appointments/<int:appointment_id>/prescribe/', views.prescribe_medicine, name='prescribe_medicine'),
    path('patient/<int:patient_id>/medical-history/', views.patient_medical_history, name='patient_medical_history'),
    path('patient/<int:patient_id>/add-medical-history/', views.add_medical_history, name='add_medical_history'),
    path('patient/<int:patient_id>/prescription-history/', views.prescription_history, name='prescription_history'),


]
