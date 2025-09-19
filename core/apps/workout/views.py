from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q

# from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from core.apps.users.models import TrainerMember
from core.apps.users.permissions.permissisons import (
    IsSuperAdmin,
    IsAdmin,
    IsTrainer,
    IsMember,
)
from core.apps.workout.models import (
    WorkoutPlan,
    Exercise,
    WorkoutPlanExercise,
    WorkoutLog,
    MemberProgress,
    WorkoutSession,
)
from core.apps.workout.serializers.serializers import (
    WorkoutPlanSerializer,
    ExerciseSerializer,
    WorkoutPlanExerciseSerializer,
    WorkoutLogSerializer,
    MemberProgressSerializer,
    WorkoutSessionSerializer,
)
from core.apps.diet.models import NutritionPlan
from core.apps.diet.serializers.serializers import NutritionPlanSerializer

User = get_user_model()


# Exercise ViewSet
class ExerciseViewSet(viewsets.ModelViewSet):
    serializer_class = ExerciseSerializer
    permission_classes = [IsSuperAdmin | IsAdmin | IsTrainer]

    def get_queryset(self):
        return Exercise.objects.filter(is_active=True).select_related()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# WorkoutPlan ViewSet
class WorkoutPlanViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutPlanSerializer
    permission_classes = [IsSuperAdmin | IsAdmin | IsTrainer | IsMember]

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return WorkoutPlan.objects.filter(is_active=True).select_related()
        elif user.role == "trainer":
            return WorkoutPlan.objects.filter(
                trainer=user, is_active=True
            ).select_related()
        else:
            return WorkoutPlan.objects.filter(
                member=user, is_active=True
            ).select_related()

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsSuperAdmin | IsAdmin | IsTrainer]
        else:
            permission_classes = [IsSuperAdmin | IsAdmin | IsTrainer | IsMember]
        return [permission() for permission in permission_classes]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# WorkoutPlanExercise ViewSet
class WorkoutPlanExerciseViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutPlanExerciseSerializer
    permission_classes = [IsSuperAdmin | IsAdmin | IsTrainer]

    def get_queryset(self):
        workout_plan_id = self.request.query_params.get("workout_plan_id")
        if workout_plan_id:
            return WorkoutPlanExercise.objects.filter(
                workout_plan_id=workout_plan_id
            ).select_related()
        return WorkoutPlanExercise.objects.all().select_related()


# WorkoutLog ViewSet
class WorkoutLogViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutLogSerializer
    permission_classes = [IsSuperAdmin | IsAdmin | IsTrainer | IsMember]

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return WorkoutLog.objects.all().select_related()
        elif user.role == "trainer":
            member_ids = TrainerMember.objects.filter(
                trainer=user, is_active=True, is_deleted=False
            ).values_list("member_id", flat=True)
            return WorkoutLog.objects.filter(member_id__in=member_ids).select_related()
        else:
            return WorkoutLog.objects.filter(member=user).select_related()


# MemberProgress ViewSet
class MemberProgressViewSet(viewsets.ModelViewSet):
    serializer_class = MemberProgressSerializer
    permission_classes = [IsSuperAdmin | IsAdmin | IsTrainer | IsMember]

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return MemberProgress.objects.all().select_related()
        elif user.role == "trainer":
            member_ids = TrainerMember.objects.filter(
                trainer=user, is_active=True, is_deleted=False
            ).values_list("member_id", flat=True)
            return MemberProgress.objects.filter(
                member_id__in=member_ids
            ).select_related()
        else:
            return MemberProgress.objects.filter(member=user).select_related()

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsSuperAdmin | IsAdmin | IsTrainer]
        else:
            permission_classes = [IsSuperAdmin | IsAdmin | IsTrainer]
        return [permission() for permission in permission_classes]


# WorkoutSession ViewSet
class WorkoutSessionViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutSessionSerializer
    permission_classes = [IsSuperAdmin | IsAdmin | IsTrainer | IsMember]

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return WorkoutSession.objects.all().select_related()
        elif user.role == "trainer":
            member_ids = TrainerMember.objects.filter(
                trainer=user, is_active=True, is_deleted=False
            ).values_list("member_id", flat=True)
            return WorkoutSession.objects.filter(
                member_id__in=member_ids
            ).select_related()
        else:
            return WorkoutSession.objects.filter(member=user).select_related()


# BMIRecommendation ViewSet
class BMIRecommendationViewSet(viewsets.ViewSet):
    permission_classes = [IsSuperAdmin | IsAdmin | IsTrainer | IsMember]

    @action(detail=False, methods=["post"], url_path="bmi")
    def bmi_recommendation(self, request):
        weight = request.data.get("weight")
        height = request.data.get("height")

        if not weight or not height:
            return Response(
                {"error": "Weight and height are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            weight = float(weight)
            height = float(height)
        except ValueError:
            return Response(
                {"error": "Weight and height must be numbers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if weight <= 0 or height <= 0:
            return Response(
                {"error": "Weight and height must be positive numbers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        bmi = weight / (height**2)
        if bmi < 18.5:
            category = "Underweight"
        elif 18.5 <= bmi < 24.9:
            category = "Normal weight"
        elif 25 <= bmi < 29.9:
            category = "Overweight"
        else:
            category = "Obese"

        if category == "Underweight":
            workout_plans = WorkoutPlan.objects.filter(
                Q(goal="muscle_gain"), is_active=True
            ).select_related()
            exercises = Exercise.objects.filter(
                Q(category="strength_training"), is_active=True
            ).select_related()
            nutrition_plans = NutritionPlan.objects.filter(
                Q(calories__gte=2500), is_active=True
            ).select_related()
        elif category == "Normal weight":
            workout_plans = WorkoutPlan.objects.filter(
                Q(goal="general_fitness"), is_active=True
            ).select_related()
            exercises = Exercise.objects.filter(
                Q(category="full_body"), is_active=True
            ).select_related()
            nutrition_plans = NutritionPlan.objects.filter(
                Q(calories__range=(2000, 2500)), is_active=True
            ).select_related()
        elif category in ["Overweight", "Obese"]:
            workout_plans = WorkoutPlan.objects.filter(
                Q(goal="general_fitness") | Q(goal="fat_loss"), is_active=True
            ).select_related()
            exercises = Exercise.objects.filter(
                Q(category="cardio"), is_active=True
            ).select_related()
            nutrition_plans = NutritionPlan.objects.filter(
                Q(calories__lte=2000), is_active=True
            ).select_related()

        return Response(
            {
                "bmi": bmi,
                "category": category,
                "workout_plans": WorkoutPlanSerializer(workout_plans, many=True).data,
                "exercises": ExerciseSerializer(exercises, many=True).data,
                "nutrition_plans": NutritionPlanSerializer(
                    nutrition_plans, many=True
                ).data,
            }
        )
