from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.apps.diet.models import (
    NutritionPlan,
)

User = get_user_model()


class NutritionPlanSerializer(serializers.ModelSerializer):
    trainer_name = serializers.CharField(source="trainer.username", read_only=True)
    member_name = serializers.CharField(source="member.username", read_only=True)

    class Meta:
        model = NutritionPlan
        fields = [
            "id",
            "trainer",
            "trainer_name",
            "member",
            "member_name",
            "name",
            "description",
            "meal_type",
            "calories",
            "protein_grams",
            "carbs_grams",
            "fat_grams",
            "meal_details",
            "is_active",
            "created_date",
        ]
        read_only_fields = ["created_date"]

    def validate_calories(self, value):
        if value <= 0:
            raise serializers.ValidationError("Calories must be greater than 0")
        return value

    def validate_protein_grams(self, value):
        if value < 0:
            raise serializers.ValidationError("Protein cannot be negative")
        return value

    def validate_carbs_grams(self, value):
        if value < 0:
            raise serializers.ValidationError("Carbs cannot be negative")
        return value

    def validate_fat_grams(self, value):
        if value < 0:
            raise serializers.ValidationError("Fat cannot be negative")
        return value

    def validate_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Plan name must be at least 3 characters long"
            )
        return value.strip()
