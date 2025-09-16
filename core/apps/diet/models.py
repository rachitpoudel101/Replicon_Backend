from django.db import models
from core.apps.users.models import User


class NutritionPlan(models.Model):
    """Nutrition plans created by trainers for members"""

    MEAL_TYPE_CHOICES = [
        ("breakfast", "Breakfast"),
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
        ("snack", "Snack"),
    ]

    class Meta:
        db_table = "nutrition_plans"

    trainer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_nutrition_plans",
        limit_choices_to={"role": "trainer"},
        help_text="Trainer who created this nutrition plan",
    )
    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="assigned_nutrition_plans",
        limit_choices_to={"role": "member"},
        help_text="Member assigned to this nutrition plan",
    )
    name = models.CharField(max_length=100, help_text="Name of the nutrition plan")
    description = models.TextField(help_text="Description of the nutrition plan")
    meal_type = models.CharField(
        max_length=20,
        choices=MEAL_TYPE_CHOICES,
        help_text="Type of meal (breakfast, lunch, dinner, snack)",
    )
    calories = models.IntegerField(help_text="Total calories for this meal")
    protein_grams = models.FloatField(help_text="Protein content in grams")
    carbs_grams = models.FloatField(help_text="Carbohydrate content in grams")
    fat_grams = models.FloatField(help_text="Fat content in grams")
    meal_details = models.TextField(
        help_text="Detailed description of the meal and ingredients"
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this nutrition plan is currently active"
    )
    created_date = models.DateTimeField(
        auto_now_add=True, help_text="Date and time when the nutrition plan was created"
    )

    def __str__(self):
        return f"{self.name} - {self.member.username} ({self.meal_type})"
