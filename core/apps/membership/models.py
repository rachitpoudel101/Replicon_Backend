from django.db import models
from core.apps.users.models import User


class Membership(models.Model):
    class Meta:
        db_table = "memberships"

    class PlanChoices(models.TextChoices):
        BASIC = "basic", "Basic"
        QUARTERLY = "quarterly", "Quarterly"
        YEARLY = "yearly", "Yearly"

    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "member"},
        help_text="Select the member for this membership",
    )
    plan_type = models.CharField(
        max_length=20,
        choices=PlanChoices.choices,
        help_text="Choose the membership plan type",
    )
    start_date = models.DateField(help_text="Membership start date")
    end_date = models.DateField(help_text="Membership end date")
    is_active = models.BooleanField(
        default=True, help_text="Whether this membership is currently active"
    )
