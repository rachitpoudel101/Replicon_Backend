from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from core.apps.users.permissions.permissisons import IsAdmin, IsTrainer, IsMember
from core.apps.membership.models import Membership
from core.apps.membership.serializers.serializers import MembershipSerializer

User = get_user_model()


class MembershipViewSet(viewsets.ModelViewSet):
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated, IsAdmin | IsTrainer | IsMember]

    def get_queryset(self):
        if self.request.user.role == "admin":
            return Membership.objects.all()
        elif self.request.user.role == "trainer":
            # Trainers can see memberships of their assigned members
            from core.apps.workout.models import TrainerMember

            member_ids = TrainerMember.objects.filter(
                trainer=self.request.user, is_active=True, is_deleted=False
            ).values_list("member_id", flat=True)
            return Membership.objects.filter(member_id__in=member_ids)
        else:
            # Members can only see their own membership
            return Membership.objects.filter(member=self.request.user)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated, IsAdmin | IsTrainer]
        else:
            permission_classes = [IsAuthenticated, IsAdmin | IsTrainer | IsMember]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if member already has an active membership
        member = serializer.validated_data["member"]
        existing_membership = Membership.objects.filter(
            member=member, is_active=True
        ).exists()

        if existing_membership:
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

        # If trying to activate membership, check if member has another active one
        if "is_active" in request.data and request.data["is_active"]:
            existing_active = (
                Membership.objects.filter(member=instance.member, is_active=True)
                .exclude(id=instance.id)
                .exists()
            )

            if existing_active:
                return Response(
                    {"error": "Member already has another active membership"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
