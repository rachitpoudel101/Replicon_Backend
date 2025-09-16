from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.apps.workout.models import (
    WorkoutPlan,
    Exercise,
    WorkoutPlanExercise,
    WorkoutLog,
    MemberProgress,
    WorkoutSession,
)

User = get_user_model()


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = "__all__"

    def validate_calories_per_minute(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Calories per minute cannot be negative")
        return value

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Exercise name must be at least 2 characters long"
            )
        return value.strip()


class WorkoutPlanExerciseSerializer(serializers.ModelSerializer):
    exercise_name = serializers.CharField(source="exercise.name", read_only=True)
    exercise_category = serializers.CharField(
        source="exercise.category", read_only=True
    )

    class Meta:
        model = WorkoutPlanExercise
        fields = [
            "id",
            "workout_plan",
            "exercise",
            "exercise_name",
            "exercise_category",
            "sets",
            "reps",
            "weight",
            "rest_time_seconds",
            "order",
            "notes",
        ]

    def validate_sets(self, value):
        if value <= 0:
            raise serializers.ValidationError("Sets must be greater than 0")
        if value > 20:
            raise serializers.ValidationError("Sets cannot exceed 20")
        return value

    def validate_reps(self, value):
        if value <= 0:
            raise serializers.ValidationError("Reps must be greater than 0")
        if value > 100:
            raise serializers.ValidationError("Reps cannot exceed 100")
        return value

    def validate_weight(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Weight cannot be negative")
        return value

    def validate_rest_time_seconds(self, value):
        if value < 0:
            raise serializers.ValidationError("Rest time cannot be negative")
        if value > 600:  # 10 minutes max
            raise serializers.ValidationError("Rest time cannot exceed 10 minutes")
        return value


class WorkoutPlanSerializer(serializers.ModelSerializer):
    trainer_name = serializers.CharField(source="trainer.username", read_only=True)
    member_name = serializers.CharField(source="member.username", read_only=True)
    plan_exercises = WorkoutPlanExerciseSerializer(many=True, read_only=True)

    class Meta:
        model = WorkoutPlan
        fields = [
            "id",
            "trainer",
            "trainer_name",
            "member",
            "member_name",
            "name",
            "description",
            "goal",
            "day_of_week",
            "duration_weeks",
            "calories_target",
            "is_active",
            "created_date",
            "updated_date",
            "plan_exercises",
        ]
        read_only_fields = ["created_date", "updated_date"]

    def validate_duration_weeks(self, value):
        if value <= 0:
            raise serializers.ValidationError("Duration must be greater than 0 weeks")
        if value > 52:
            raise serializers.ValidationError("Duration cannot exceed 52 weeks")
        return value

    def validate_calories_target(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Calories target must be greater than 0")
        return value

    def validate_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Plan name must be at least 3 characters long"
            )
        return value.strip()


class WorkoutLogSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source="member.username", read_only=True)
    exercise_name = serializers.CharField(source="exercise.name", read_only=True)
    workout_plan_name = serializers.CharField(
        source="workout_plan.name", read_only=True
    )

    class Meta:
        model = WorkoutLog
        fields = [
            "id",
            "member",
            "member_name",
            "workout_plan",
            "workout_plan_name",
            "exercise",
            "exercise_name",
            "date",
            "sets_completed",
            "reps_completed",
            "weight_used",
            "notes",
            "duration_minutes",
        ]
        read_only_fields = ["date"]

    def validate_sets_completed(self, value):
        if value <= 0:
            raise serializers.ValidationError("Sets completed must be greater than 0")
        return value

    def validate_reps_completed(self, value):
        if value <= 0:
            raise serializers.ValidationError("Reps completed must be greater than 0")
        return value

    def validate_weight_used(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Weight used cannot be negative")
        return value

    def validate_duration_minutes(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Duration must be greater than 0 minutes")
        return value


class MemberProgressSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source="member.username", read_only=True)

    class Meta:
        model = MemberProgress
        fields = [
            "id",
            "member",
            "member_name",
            "weight",
            "body_fat_percentage",
            "muscle_mass",
            "measurements",
            "progress_photos",
            "notes",
            "recorded_date",
        ]
        read_only_fields = ["recorded_date"]

    def validate_weight(self, value):
        if value <= 0:
            raise serializers.ValidationError("Weight must be greater than 0")
        if value > 500:  # reasonable upper limit
            raise serializers.ValidationError("Weight cannot exceed 500kg")
        return value

    def validate_body_fat_percentage(self, value):
        if value is not None:
            if value < 0 or value > 100:
                raise serializers.ValidationError(
                    "Body fat percentage must be between 0 and 100"
                )
        return value

    def validate_muscle_mass(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Muscle mass must be greater than 0")
        return value


class WorkoutSessionSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source="member.username", read_only=True)
    workout_plan_name = serializers.CharField(
        source="workout_plan.name", read_only=True
    )
    duration_minutes = serializers.ReadOnlyField()

    class Meta:
        model = WorkoutSession
        fields = [
            "id",
            "member",
            "member_name",
            "workout_plan",
            "workout_plan_name",
            "start_time",
            "end_time",
            "total_calories_burned",
            "completed",
            "rating",
            "feedback",
            "created_date",
            "duration_minutes",
        ]
        read_only_fields = ["created_date", "duration_minutes"]

    def validate(self, data):
        if "end_time" in data and data["end_time"] and "start_time" in data:
            if data["end_time"] <= data["start_time"]:
                raise serializers.ValidationError("End time must be after start time")
        return data

    def validate_total_calories_burned(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Calories burned cannot be negative")
        return value

    def validate_rating(self, value):
        if value is not None:
            if value < 1 or value > 5:
                raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
