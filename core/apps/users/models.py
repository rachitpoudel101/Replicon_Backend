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

    role = models.CharField(
        max_length=50,
        choices=RolesChoices.choices,
        help_text="User role in the system (admin, trainer, or member)",
    )
    bio = models.TextField(
        blank=True, null=True, help_text="User's biography or description"
    )
    gender = models.CharField(
        max_length=10,
        choices=GenderChoices.choices,
        blank=True,
        null=True,
        help_text="User's gender",
    )
    phone = models.CharField(
        max_length=15, blank=True, null=True, help_text="User's phone number"
    )
    weight = models.FloatField(
        blank=True, null=True, help_text="User's weight in kilograms"
    )
    height = models.FloatField(
        blank=True, null=True, help_text="User's height in centimeters"
    )
    age = models.PositiveIntegerField(
        blank=True, null=True, help_text="User's age in years"
    )
    profile_image = models.ImageField(
        upload_to="profile_images/",
        blank=True,
        null=True,
        help_text="User's profile picture",
    )
    is_deleted = models.BooleanField(
        default=False, help_text="Soft delete flag for this user"
    )
    is_super = models.BooleanField(
        default=False, help_text="Whether this user has super admin privileges"
    )
