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


class TrainerMember(models.Model):
    class Meta:
        db_table = "trainer_members"
        unique_together = ("trainer", "member")

    trainer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="trainer_members",
        limit_choices_to={"role": "trainer"},
        help_text="Select the trainer for this member assignment",
    )
    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="member_trainer",
        limit_choices_to={"role": "member"},
        help_text="Select the member to be assigned to this trainer",
    )
    assigned_date = models.DateField(
        auto_now_add=True, help_text="Date when the member was assigned to the trainer"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this trainer-member relationship is currently active",
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about this trainer-member assignment",
    )
    is_deleted = models.BooleanField(
        default=False, help_text="Soft delete flag for this assignment"
    )