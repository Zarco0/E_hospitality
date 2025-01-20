from django.db import models

# Create your models here.

class HealthResource(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    content = models.TextField()  # Detailed content of the resource
    category = models.CharField(max_length=100, choices=[('Nutrition', 'Nutrition'), ('Mental Health', 'Mental Health')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    contact_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='departments')

    def __str__(self):
        return f"{self.name} ({self.location.name})"


class Resource(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='resources')
    quantity = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.department.name})"

