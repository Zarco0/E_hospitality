from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):

    ROLE_CHOICES = [
        ('Patient','Patient'),
        ('Doctor','Doctor'),
        ('Admin','Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Patient')
    username = models.CharField(max_length=150, unique=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.jpg')
    specialization = models.CharField(max_length=200, blank=True, null=True)
    is_blocked = models.BooleanField(default=False)
    appointment_fee = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)  # Add this if missing



    def is_patient(self):
        return self.role == 'Patient'

    def is_doctor(self):
        return self.role == 'Doctor'

    def is_admin(self):
        return self.role == 'Admin'
    