from django.urls import path
from . import views

app_name = 'patient'

urlpatterns = [
    path('appointments/', views.appointments, name='appointments'),
    path('appointments/book/', views.book_appointment, name='book_appointment'),
    path('appointments/cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('appointments/reschedule/<int:appointment_id>/', views.reschedule_appointment, name='reschedule_appointment'),
    path('facilities/', views.view_facilities, name='view_facilities'),
    path('facilities/department/<int:department_id>/', views.department_details, name='department_details'),
    path('medical-history/', views.medical_history, name='medical_history'),
    path('patients/billing/<int:appointment_id>/', views.billing, name='billing'),
    path('health-resources/', views.view_health_resources, name='view_resources'),
    path('billing/', views.list_billings, name='list_billings'),
    path('billing/<int:billing_id>/checkout/', views.create_checkout_session, name='checkout'),
    path('billing/<int:billing_id>/success/', views.payment_success, name='payment_success'),
    path('billing/<int:billing_id>/cancel/', views.payment_cancel, name='payment_cancel'),
    


]
