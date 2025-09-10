from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('trainer', 'Trainer'),
        ('member', 'Member'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    phone = models.CharField(max_length=15, blank=True, null=True)