from django.db import models

from accounts.models import CustomUser
from patients.models import Appointment
from django.utils.timezone import now

class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="prescription",null=True,blank=True)
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="prescriptions")
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="received_prescriptions")
    date = models.DateTimeField(default=now)
    medications = models.TextField(help_text="List medications separated by commas.")
    instructions = models.TextField(help_text="Additional instructions for the patient.", blank=True, null=True)

    def __str__(self):
        return f"Prescription for {self.patient.username} by {self.doctor.username}"