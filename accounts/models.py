from django.db import models
from django.contrib.auth.models import AbstractUser


    
from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class State(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class District(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

# Extend your custom User model here if needed

class User(AbstractUser):
    is_manager = models.BooleanField('Is manager', default=False)
    is_trainer = models.BooleanField('Is trainer', default=False)
    is_student = models.BooleanField('Is student', default=False)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    
    @property
    def role(self):
     if self.is_student:
        return "student"
     elif self.is_trainer:
        return "trainer"
     elif self.is_manager:
        return "manager"
     return "unknown"

    
    
from django.db import models
from django.conf import settings

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='student_profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


