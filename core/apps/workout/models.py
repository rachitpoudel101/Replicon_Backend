from django.db import models
from core.apps.users.models import User
class TrainerMember(models.Model):
    class Meta:
        db_table = "trainer_members"
        unique_together = ("trainer", "member")

    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trainer_members", limit_choices_to={'role': 'trainer'})
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="member_trainer", limit_choices_to={'role': 'member'})
    assigned_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

class WorkoutPlan(models.Model):
    GOAL_CHOICES = [
        ('fat_loss', 'Fat Loss'),
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('strength', 'Strength Training'),
        ('endurance', 'Endurance'),
        ('general_fitness', 'General Fitness'),
    ]
    
    DAY_CHOICES = [
        ('sunday', 'Sunday'),
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
    ]

    class Meta:
        db_table = "workout_plans"

    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_workout_plans", limit_choices_to={'role': 'trainer'})
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assigned_workout_plans", limit_choices_to={'role': 'member'})
    name = models.CharField(max_length=100)
    description = models.TextField()
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES)
    day_of_week = models.CharField(max_length=20, choices=DAY_CHOICES)
    duration_weeks = models.IntegerField(default=4)  # Plan duration
    calories_target = models.IntegerField(blank=True, null=True)  # Target calories to burn
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.member.username} ({self.day_of_week})"

class Exercise(models.Model):
    CATEGORY_CHOICES = [
        ('chest', 'Chest'),
        ('back', 'Back'),
        ('shoulders', 'Shoulders'),
        ('biceps', 'Biceps'),
        ('triceps', 'Triceps'),
        ('legs', 'Legs'),
        ('abs', 'Abs'),
        ('cardio', 'Cardio'),
        ('full_body', 'Full Body'),
    ]

    class Meta:
        db_table = "exercises"

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)
    muscle_groups = models.CharField(max_length=200)  # e.g., 'chest, triceps, shoulders'
    equipment_needed = models.CharField(max_length=200, blank=True, null=True)
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ], default='beginner')
    calories_per_minute = models.FloatField(blank=True, null=True)
    exercise_image = models.ImageField(upload_to="exercise_images/", blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.category})"

class WorkoutPlanExercise(models.Model):
    class Meta:
        db_table = "workout_plan_exercises"
        unique_together = ("workout_plan", "exercise", "order")

    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name="plan_exercises")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.IntegerField()
    reps = models.IntegerField()
    weight = models.FloatField(blank=True, null=True)  # Optional for bodyweight exercises
    rest_time_seconds = models.IntegerField(default=60)  # Rest time between sets
    order = models.IntegerField()  # Order of exercise in the workout
    notes = models.TextField(blank=True, null=True)  # Special instructions for this exercise

class WorkoutLog(models.Model):
    class Meta:
        db_table = "workout_logs"

    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="workout_logs", limit_choices_to={'role': 'member'})
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name="logs", blank=True, null=True)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    sets_completed = models.IntegerField()
    reps_completed = models.IntegerField()
    weight_used = models.FloatField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    duration_minutes = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.member.username} - {self.exercise.name} on {self.date}"

class MemberProgress(models.Model):
    """Track member's physical progress over time"""
    class Meta:
        db_table = "member_progress"

    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="progress_records", limit_choices_to={'role': 'member'})
    weight = models.FloatField()
    body_fat_percentage = models.FloatField(blank=True, null=True)
    muscle_mass = models.FloatField(blank=True, null=True)
    measurements = models.JSONField(blank=True, null=True)  # Store chest, waist, hip measurements
    progress_photos = models.ImageField(upload_to="progress_photos/", blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    recorded_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.username} - {self.weight}kg on {self.recorded_date}"

class NutritionPlan(models.Model):
    """Nutrition plans created by trainers for members"""
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]

    class Meta:
        db_table = "nutrition_plans"

    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_nutrition_plans", limit_choices_to={'role': 'trainer'})
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assigned_nutrition_plans", limit_choices_to={'role': 'member'})
    name = models.CharField(max_length=100)
    description = models.TextField()
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    calories = models.IntegerField()
    protein_grams = models.FloatField()
    carbs_grams = models.FloatField()
    fat_grams = models.FloatField()
    meal_details = models.TextField()  # Description of the meal
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.member.username} ({self.meal_type})"

class WorkoutSession(models.Model):
    """Complete workout session tracking"""
    class Meta:
        db_table = "workout_sessions"

    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="workout_sessions", limit_choices_to={'role': 'member'})
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name="sessions")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    total_calories_burned = models.IntegerField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    rating = models.IntegerField(blank=True, null=True)  # 1-5 rating
    feedback = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.username} - {self.workout_plan.name} on {self.start_time.date()}"

    @property
    def duration_minutes(self):
        if self.end_time:
            return int((self.end_time - self.start_time).total_seconds() / 60)
        return None