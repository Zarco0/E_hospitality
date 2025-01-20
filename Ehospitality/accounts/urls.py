from django.urls import path
from .views import *

app_name = 'accounts'


urlpatterns = [
    path('register/', patient_register, name='register'),
    path('', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('patient-dashboard/', patient_dashboard, name='patient_dashboard'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('doctor-dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('facility_management/', facility_management, name='facility_management'),
    

    
]
