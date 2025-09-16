from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from core.apps.users.permissions.permissisons import (
    IsSuperAdmin,
    IsAdmin,
    IsTrainer,
    IsMember,
)
from core.apps.diet.models import NutritionPlan
from core.apps.diet.serializers.serializers import (
    NutritionPlanSerializer,
)

User = get_user_model()


# NutritionPlan ViewSet
class NutritionPlanViewSet(viewsets.ModelViewSet):
    serializer_class = NutritionPlanSerializer
    permission_classes = [IsSuperAdmin | IsAdmin | IsTrainer | IsMember]

    def get_queryset(self):
        user = self.request.user

        # Check if the user is a superuser
        if user.is_super:
            return NutritionPlan.objects.all()

        # Check for other roles
        if user.role == "admin":
            return NutritionPlan.objects.filter(is_active=True)
        elif user.role == "trainer":
            return NutritionPlan.objects.filter(trainer=user, is_active=True)
        else:
            return NutritionPlan.objects.filter(member=user, is_active=True)

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
