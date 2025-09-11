from django.db import models
from core.apps.users.models import User


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


class WorkoutPlan(models.Model):
    GOAL_CHOICES = [
        ("fat_loss", "Fat Loss"),
        ("weight_loss", "Weight Loss"),
        ("muscle_gain", "Muscle Gain"),
        ("strength", "Strength Training"),
        ("endurance", "Endurance"),
        ("general_fitness", "General Fitness"),
    ]

    DAY_CHOICES = [
        ("sunday", "Sunday"),
        ("monday", "Monday"),
        ("tuesday", "Tuesday"),
        ("wednesday", "Wednesday"),
        ("thursday", "Thursday"),
        ("friday", "Friday"),
    ]

    class Meta:
        db_table = "workout_plans"

    trainer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_workout_plans",
        limit_choices_to={"role": "trainer"},
        help_text="Trainer who created this workout plan",
    )
    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="assigned_workout_plans",
        limit_choices_to={"role": "member"},
        help_text="Member assigned to this workout plan",
    )
    name = models.CharField(max_length=100, help_text="Name of the workout plan")
    description = models.TextField(help_text="Detailed description of the workout plan")
    goal = models.CharField(
        max_length=20,
        choices=GOAL_CHOICES,
        help_text="Primary fitness goal of this workout plan",
    )
    day_of_week = models.CharField(
        max_length=20,
        choices=DAY_CHOICES,
        help_text="Day of the week when this workout should be performed",
    )
    duration_weeks = models.IntegerField(
        default=4, help_text="Duration of the workout plan in weeks"
    )
    calories_target = models.IntegerField(
        blank=True, null=True, help_text="Target calories to burn during this workout"
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this workout plan is currently active"
    )
    created_date = models.DateTimeField(
        auto_now_add=True, help_text="Date and time when the workout plan was created"
    )
    updated_date = models.DateTimeField(
        auto_now=True, help_text="Date and time when the workout plan was last updated"
    )

    def __str__(self):
        return f"{self.name} - {self.member.username} ({self.day_of_week})"


class Exercise(models.Model):
    CATEGORY_CHOICES = [
        ("chest", "Chest"),
        ("back", "Back"),
        ("shoulders", "Shoulders"),
        ("biceps", "Biceps"),
        ("triceps", "Triceps"),
        ("legs", "Legs"),
        ("abs", "Abs"),
        ("cardio", "Cardio"),
        ("full_body", "Full Body"),
    ]

    class Meta:
        db_table = "exercises"

    name = models.CharField(max_length=100, help_text="Name of the exercise")
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        help_text="Category/muscle group targeted by this exercise",
    )
    description = models.TextField(
        blank=True, null=True, help_text="Brief description of the exercise"
    )
    instructions = models.TextField(
        blank=True,
        null=True,
        help_text="Step-by-step instructions for performing the exercise",
    )
    muscle_groups = models.CharField(
        max_length=200,
        help_text="Comma-separated list of muscle groups targeted (e.g., 'chest, triceps, shoulders')",
    )
    equipment_needed = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Equipment required to perform this exercise",
    )
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ("beginner", "Beginner"),
            ("intermediate", "Intermediate"),
            ("advanced", "Advanced"),
        ],
        default="beginner",
        help_text="Difficulty level of the exercise",
    )
    calories_per_minute = models.FloatField(
        blank=True,
        null=True,
        help_text="Estimated calories burned per minute during this exercise",
    )
    exercise_image = models.ImageField(
        upload_to="exercise_images/",
        blank=True,
        null=True,
        help_text="Image demonstrating the exercise",
    )
    video_url = models.URLField(
        blank=True, null=True, help_text="URL to a video demonstration of the exercise"
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this exercise is currently available for use"
    )
    created_date = models.DateTimeField(
        auto_now_add=True, help_text="Date and time when the exercise was created"
    )

    def __str__(self):
        return f"{self.name} ({self.category})"


class WorkoutPlanExercise(models.Model):
    class Meta:
        db_table = "workout_plan_exercises"
        unique_together = ("workout_plan", "exercise", "order")

    workout_plan = models.ForeignKey(
        WorkoutPlan,
        on_delete=models.CASCADE,
        related_name="plan_exercises",
        help_text="Workout plan this exercise belongs to",
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        help_text="Exercise to be included in the workout plan",
    )
    sets = models.IntegerField(help_text="Number of sets to perform for this exercise")
    reps = models.IntegerField(help_text="Number of repetitions per set")
    weight = models.FloatField(
        blank=True,
        null=True,
        help_text="Weight to be used for this exercise (optional for bodyweight exercises)",
    )
    rest_time_seconds = models.IntegerField(
        default=60, help_text="Rest time in seconds between sets"
    )
    order = models.IntegerField(
        help_text="Order/sequence of this exercise in the workout plan"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Special instructions or notes for this exercise",
    )


class WorkoutLog(models.Model):
    class Meta:
        db_table = "workout_logs"

    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="workout_logs",
        limit_choices_to={"role": "member"},
        help_text="Member who performed this workout",
    )
    workout_plan = models.ForeignKey(
        WorkoutPlan,
        on_delete=models.CASCADE,
        related_name="logs",
        blank=True,
        null=True,
        help_text="Workout plan this log entry belongs to (optional)",
    )
    exercise = models.ForeignKey(
        Exercise, on_delete=models.CASCADE, help_text="Exercise that was performed"
    )
    date = models.DateField(
        auto_now_add=True, help_text="Date when the workout was performed"
    )
    sets_completed = models.IntegerField(help_text="Number of sets actually completed")
    reps_completed = models.IntegerField(
        help_text="Number of repetitions actually completed"
    )
    weight_used = models.FloatField(
        blank=True, null=True, help_text="Weight used during the exercise"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the workout performance",
    )
    duration_minutes = models.IntegerField(
        blank=True, null=True, help_text="Duration of the exercise in minutes"
    )

    def __str__(self):
        return f"{self.member.username} - {self.exercise.name} on {self.date}"


class MemberProgress(models.Model):
    """Track member's physical progress over time"""

    class Meta:
        db_table = "member_progress"

    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="progress_records",
        limit_choices_to={"role": "member"},
        help_text="Member whose progress is being tracked",
    )
    weight = models.FloatField(help_text="Current weight in kilograms")
    body_fat_percentage = models.FloatField(
        blank=True, null=True, help_text="Body fat percentage"
    )
    muscle_mass = models.FloatField(
        blank=True, null=True, help_text="Muscle mass in kilograms"
    )
    measurements = models.JSONField(
        blank=True,
        null=True,
        help_text="Body measurements (chest, waist, hip, etc.) in JSON format",
    )
    progress_photos = models.ImageField(
        upload_to="progress_photos/",
        blank=True,
        null=True,
        help_text="Progress photos to track visual changes",
    )
    notes = models.TextField(
        blank=True, null=True, help_text="Additional notes about the progress record"
    )
    recorded_date = models.DateField(
        auto_now_add=True, help_text="Date when this progress was recorded"
    )

    def __str__(self):
        return f"{self.member.username} - {self.weight}kg on {self.recorded_date}"


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


class WorkoutSession(models.Model):
    """Complete workout session tracking"""

    class Meta:
        db_table = "workout_sessions"

    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="workout_sessions",
        limit_choices_to={"role": "member"},
        help_text="Member performing this workout session",
    )
    workout_plan = models.ForeignKey(
        WorkoutPlan,
        on_delete=models.CASCADE,
        related_name="sessions",
        help_text="Workout plan being followed in this session",
    )
    start_time = models.DateTimeField(
        help_text="Date and time when the workout session started"
    )
    end_time = models.DateTimeField(
        blank=True, null=True, help_text="Date and time when the workout session ended"
    )
    total_calories_burned = models.IntegerField(
        blank=True, null=True, help_text="Total calories burned during the session"
    )
    completed = models.BooleanField(
        default=False, help_text="Whether the workout session was completed"
    )
    rating = models.IntegerField(
        blank=True, null=True, help_text="Session rating on a scale of 1-5"
    )
    feedback = models.TextField(
        blank=True, null=True, help_text="Member's feedback about the workout session"
    )
    created_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when this session record was created",
    )

    def __str__(self):
        return f"{self.member.username} - {self.workout_plan.name} on {self.start_time.date()}"

    @property
    def duration_minutes(self):
        if self.end_time:
            return int((self.end_time - self.start_time).total_seconds() / 60)
        return None
