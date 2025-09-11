from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Meta:
        db_table = "users"

    class GenderChoices(models.TextChoices):
        MALE = "male"
        FEMALE = "female"
        OTHER = "other"

    class RolesChoices(models.TextChoices):
        ADMIN = "admin"
        TRAINER = "trainer"
        MEMBER = "member"

    role = models.CharField(max_length=50, choices=RolesChoices.choices)
    bio = models.TextField(blank=True, null=True)
    gender = models.CharField(
        max_length=10, choices=GenderChoices.choices, blank=True, null=True
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    profile_image = models.ImageField(
        upload_to="profile_images/", blank=True, null=True
    )
    is_deleted = models.BooleanField(default=False)
    is_super = models.BooleanField(default=False)
