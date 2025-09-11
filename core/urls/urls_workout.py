from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.apps.workout.views import (
    TrainerMemberViewSet,
    ExerciseViewSet,
    WorkoutPlanViewSet,
    WorkoutPlanExerciseViewSet,
    WorkoutLogViewSet,
    MemberProgressViewSet,
    NutritionPlanViewSet,
    WorkoutSessionViewSet,
)

# Create a router and register viewsets
router = DefaultRouter()
router.register(r"trainer-members", TrainerMemberViewSet, basename="trainermember")
router.register(r"exercises", ExerciseViewSet, basename="exercise")
router.register(r"workout-plans", WorkoutPlanViewSet, basename="workoutplan")
router.register(
    r"workout-plan-exercises",
    WorkoutPlanExerciseViewSet,
    basename="workoutplanexercise",
)
router.register(r"workout-logs", WorkoutLogViewSet, basename="workoutlog")
router.register(r"member-progress", MemberProgressViewSet, basename="memberprogress")
router.register(r"nutrition-plans", NutritionPlanViewSet, basename="nutritionplan")
router.register(r"workout-sessions", WorkoutSessionViewSet, basename="workoutsession")

# URL patterns
urlpatterns = [
    path("", include(router.urls)),
]
