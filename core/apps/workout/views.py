from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from core.apps.users.permissions.permissisons import IsAdmin, IsTrainer, IsMember
from core.apps.workout.models import (
    TrainerMember,
    WorkoutPlan,
    Exercise,
    WorkoutPlanExercise,
    WorkoutLog,
    MemberProgress,
    NutritionPlan,
    WorkoutSession,
)
from core.apps.workout.serializers.serializers import (
    TrainerMemberSerializer,
    WorkoutPlanSerializer,
    ExerciseSerializer,
    WorkoutPlanExerciseSerializer,
    WorkoutLogSerializer,
    MemberProgressSerializer,
    NutritionPlanSerializer,
    WorkoutSessionSerializer,
)

User = get_user_model()


# TrainerMember ViewSet
class TrainerMemberViewSet(viewsets.ModelViewSet):
    serializer_class = TrainerMemberSerializer
    permission_classes = [IsAdmin | IsTrainer]

    def get_queryset(self):
        if self.request.user.role == "admin":
            return TrainerMember.objects.filter(is_deleted=False)
        elif self.request.user.role == "trainer":
            return TrainerMember.objects.filter(
                trainer=self.request.user, is_deleted=False
            )
        else:
            return TrainerMember.objects.filter(
                member=self.request.user, is_deleted=False
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Exercise ViewSet
class ExerciseViewSet(viewsets.ModelViewSet):
    serializer_class = ExerciseSerializer
    permission_classes = [IsAdmin | IsTrainer]

    def get_queryset(self):
        return Exercise.objects.filter(is_active=True)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# WorkoutPlan ViewSet
class WorkoutPlanViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutPlanSerializer
    permission_classes = [IsAdmin | IsTrainer | IsMember]

    def get_queryset(self):
        if self.request.user.role == "admin":
            return WorkoutPlan.objects.filter(is_active=True)
        elif self.request.user.role == "trainer":
            return WorkoutPlan.objects.filter(trainer=self.request.user, is_active=True)
        else:
            return WorkoutPlan.objects.filter(member=self.request.user, is_active=True)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsAdmin | IsTrainer]
        else:
            permission_classes = [IsAdmin | IsTrainer | IsMember]
        return [permission() for permission in permission_classes]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# WorkoutPlanExercise ViewSet
class WorkoutPlanExerciseViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutPlanExerciseSerializer
    permission_classes = [IsAdmin | IsTrainer]

    def get_queryset(self):
        workout_plan_id = self.request.query_params.get("workout_plan_id")
        if workout_plan_id:
            return WorkoutPlanExercise.objects.filter(workout_plan_id=workout_plan_id)
        return WorkoutPlanExercise.objects.all()


# WorkoutLog ViewSet
class WorkoutLogViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutLogSerializer
    permission_classes = [IsAdmin | IsTrainer | IsMember]

    def get_queryset(self):
        if self.request.user.role == "admin":
            return WorkoutLog.objects.all()
        elif self.request.user.role == "trainer":
            member_ids = TrainerMember.objects.filter(
                trainer=self.request.user, is_active=True, is_deleted=False
            ).values_list("member_id", flat=True)
            return WorkoutLog.objects.filter(member_id__in=member_ids)
        else:
            return WorkoutLog.objects.filter(member=self.request.user)


# MemberProgress ViewSet
class MemberProgressViewSet(viewsets.ModelViewSet):
    serializer_class = MemberProgressSerializer
    permission_classes = [IsAdmin | IsTrainer | IsMember]

    def get_queryset(self):
        if self.request.user.role == "admin":
            return MemberProgress.objects.all()
        elif self.request.user.role == "trainer":
            member_ids = TrainerMember.objects.filter(
                trainer=self.request.user, is_active=True, is_deleted=False
            ).values_list("member_id", flat=True)
            return MemberProgress.objects.filter(member_id__in=member_ids)
        else:
            return MemberProgress.objects.filter(member=self.request.user)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsAdmin | IsTrainer]
        else:
            permission_classes = [IsAdmin | IsTrainer | IsMember]
        return [permission() for permission in permission_classes]


# NutritionPlan ViewSet
class NutritionPlanViewSet(viewsets.ModelViewSet):
    serializer_class = NutritionPlanSerializer
    permission_classes = [IsAdmin | IsTrainer | IsMember]

    def get_queryset(self):
        if self.request.user.role == "admin":
            return NutritionPlan.objects.filter(is_active=True)
        elif self.request.user.role == "trainer":
            return NutritionPlan.objects.filter(
                trainer=self.request.user, is_active=True
            )
        else:
            return NutritionPlan.objects.filter(
                member=self.request.user, is_active=True
            )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsAdmin | IsTrainer]
        else:
            permission_classes = [IsAdmin | IsTrainer | IsMember]
        return [permission() for permission in permission_classes]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# WorkoutSession ViewSet
class WorkoutSessionViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutSessionSerializer
    permission_classes = [IsAdmin | IsTrainer | IsMember]

    def get_queryset(self):
        if self.request.user.role == "admin":
            return WorkoutSession.objects.all()
        elif self.request.user.role == "trainer":
            member_ids = TrainerMember.objects.filter(
                trainer=self.request.user, is_active=True, is_deleted=False
            ).values_list("member_id", flat=True)
            return WorkoutSession.objects.filter(member_id__in=member_ids)
        else:
            return WorkoutSession.objects.filter(member=self.request.user)
