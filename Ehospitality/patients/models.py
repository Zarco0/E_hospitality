from django.db import models
from django.conf import settings
from accounts.models import CustomUser


class Appointment(models.Model):
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    doctor = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="appointments"
    )
    date = models.DateTimeField()
    reason = models.TextField()
    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('canceled', 'Canceled'),
            ('failed', 'Failed'),
        ],
        default='scheduled'
    )
    appointment_fee = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)

    def __str__(self):
        return f"Appointment for {self.patient.username} with {self.doctor.username} on {self.date}"

    def cancel(self):
        self.status = 'canceled'
        self.save()

    def reschedule(self, new_date):
        self.date = new_date
        self.save()

    @property
    def payment_status(self):
        # Access payment_status from related Billing instance
        if hasattr(self, 'billing'):
            return self.billing.payment_status
        return 'pending'  # Default if no Billing instance exists



class Billing(models.Model):
    appointment = models.OneToOneField(
        Appointment, on_delete=models.CASCADE, related_name='billing'
    )
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed')],
        default='pending'
    )
    payment_date = models.DateTimeField(blank=True, null=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Billing for Appointment #{self.appointment.id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Sync appointment status based on payment status
        if self.payment_status == 'paid':
            self.appointment.status = 'confirmed'
        elif self.payment_status == 'failed':
            self.appointment.status = 'failed'
        else:
            self.appointment.status = 'pending'
        self.appointment.save()


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Appointment)
def create_billing_for_appointment(sender, instance, created, **kwargs):
    if created:  # Only create billing for new appointments
        Billing.objects.create(
            appointment=instance,
            patient=instance.patient,
            amount=instance.appointment_fee,
            payment_status='pending'
        )

class MedicalHistory(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Diagnoses
    diagnoses = models.ManyToManyField('Diagnosis', blank=True)
    
    # Medications
    medications = models.ManyToManyField('Medication', blank=True)
    
    # Allergies
    allergies = models.ManyToManyField('Allergy', blank=True)
    
    # Treatments
    treatments = models.ManyToManyField('Treatment', blank=True)

class Diagnosis(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField()

class Medication(models.Model):
    name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=200)

class Allergy(models.Model):
    name = models.CharField(max_length=200)
    severity = models.CharField(max_length=200)

class Treatment(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField()
    result = models.CharField(max_length=200)



    def __str__(self):
        return f"Billing for {self.appointment} - {self.patient}"

