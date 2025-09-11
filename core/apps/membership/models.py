from django.db import models
from core.apps.users.models import User
class Membership(models.Model):
    class Meta:
        db_table = "memberships"
    class PlanChopices(models.TextChoices):
        ModuleNotFoundError = "basic"
        QUARTARLY = "quarterly"
        YEARLY = "yearly"
    member = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'member'})
    plan_type = models.CharField(max_length=20, choices=PlanChopices.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)