from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth import get_user_model

from core.apps.users.permissions.permissisons import (
    IsSuperAdmin,
    IsAdmin,
    IsTrainer,
    IsMember,
)
from core.apps.membership.models import Membership
from core.apps.membership.serializers.serializers import MembershipSerializer

User = get_user_model()


class MembershipViewSet(viewsets.ModelViewSet):
    serializer_class = MembershipSerializer
    permission_classes = [IsSuperAdmin | IsAdmin | IsTrainer | IsMember]

    def get_queryset(self):
        """Return optimized queryset depending on user role."""
        user = self.request.user
        role = getattr(user, "role", None)

        # Optimize queryset with select_related for member (avoid N+1 queries)
        base_qs = Membership.objects.select_related("member")

        # SuperAdmin or Admin → full access
        if getattr(user, "is_super", False) or role == "admin":
            return base_qs

        # Trainer → only memberships of assigned members
        if role == "trainer":
            from core.apps.workout.models import TrainerMember

            member_ids = TrainerMember.objects.filter(
                trainer=user, is_active=True, is_deleted=False
            ).values_list("member_id", flat=True)
            return base_qs.filter(member_id__in=member_ids)

        # Member → only own memberships
        if role == "member":
            return base_qs.filter(member=user)

        # No access by default
        return Membership.objects.none()

    def get_permissions(self):
        """Restrict create/update/delete to Admins/Trainers."""
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsSuperAdmin | IsAdmin | IsTrainer]
        else:
            permission_classes = [IsSuperAdmin | IsAdmin | IsTrainer | IsMember]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        member = serializer.validated_data["member"]

        # Optimized existence check (only fetch ID)
        if Membership.objects.filter(member=member, is_active=True).only("id").exists():
            return Response(
                {"error": "Member already has an active membership"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # If activating membership → ensure no other active one exists
        if request.data.get("is_active", False):
            if (
                Membership.objects.filter(member=instance.member, is_active=True)
                .exclude(id=instance.id)
                .only("id")
                .exists()
            ):
                return Response(
                    {"error": "Member already has another active membership"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Soft-delete: deactivate instead of removing record."""
        instance = self.get_object()
        if instance.is_active:
            instance.is_active = False
            instance.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)
