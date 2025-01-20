from django.urls import path
from . import views
from.views import *

app_name = 'admins'

urlpatterns = [
    path('assign-role/<int:user_id>/<str:role>/', assign_role, name='assign_role'),
    path('list-users/', list_users, name='list_users'),
    path('block-user/<int:user_id>/', block_user, name='block_user'),  
    path('unblock-user/<int:user_id>/', unblock_user, name='unblock_user'),
    path('health-resources/', views.manage_health_resources, name='manage_resources'),
    path('health-resources/add/', views.add_health_resource, name='add_resource'),
    path('health-resources/delete/<int:resource_id>/', views.delete_health_resource, name='delete_resource'),
    path('appointment_management/', appointment_management, name='appointment_management'),
    path('locations/', views.manage_locations, name='manage_locations'),
    path('locations/add/', views.add_location, name='add_location'),
    path('departments/', views.manage_departments, name='manage_departments'),
    path('departments/add/', views.add_department, name='add_department'),
    path('resources/', views.manage_resources, name='manage_resources'),
    path('resources/add/', views.add_resource, name='add_resource'),
    path('appointments/', views.appointment_list, name='appointments_list'),
    path('appointments/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('appointments/reschedule/<int:appointment_id>/', views.reschedule_appointment, name='reschedule_appointment'),

]
