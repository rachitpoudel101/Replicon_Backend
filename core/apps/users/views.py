import traceback
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.decorators import action
from core.apps.users.permissions.permissisons import IsSuperAdmin, IsAdmin, IsTrainer
from core.apps.users.models import TrainerMember, User
from core.apps.users.serializers.serializers import (
    LogoutSerializer,
    SelfAPISerilizer,
    TrainerMemberSerializer,
    UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_deleted=False)  # Only show non-deleted users
    serializer_class = UserSerializer
    permission_classes = [IsSuperAdmin | IsAdmin | IsTrainer]

    def get_queryset(self):
        """Override to filter out deleted users by default"""
        return User.objects.filter(is_deleted=False)

    def create(self, request, *args, **kwargs):
        """Create a new user with proper validation"""
        data = request.data.copy()

        # Check for basic required fields
        required_fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "role",
        ]
        missing_fields = []

        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)

        # Check role-specific required fields
        role = data.get("role")
        if role in ["trainer", "member"]:
            additional_required_fields = [
                "age",
                "weight",
                "height",
                "phone",
                "bio",
                "gender",
            ]
            for field in additional_required_fields:
                if field not in data or not data[field]:
                    missing_fields.append(field)

            # Check for profile_image
            if "profile_image" not in request.FILES:
                missing_fields.append("profile_image")

        if missing_fields:
            return Response(
                {"error": f"Required fields missing: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate data using serializer (with password included)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Create user manually with hashed password
        validated_data = serializer.validated_data
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return Response(
            {"message": "User created successfully", "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        """Update user with proper validation"""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        data = request.data.copy()

        # Handle password separately
        password = data.pop("password", None)

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Update user manually
        validated_data = serializer.validated_data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        return Response(
            {
                "message": "User updated successfully",
                "user": UserSerializer(instance).data,
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        """Soft delete user by setting is_deleted=True"""
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(
            {"message": "User deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )

    def retrieve(self, request, *args, **kwargs):
        """Get single user details"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {"message": "User retrieved successfully", "user": serializer.data},
            status=status.HTTP_200_OK,
        )

    def list(self, request, *args, **kwargs):
        """List all non-deleted users"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {"message": "Users retrieved successfully", "users": serializer.data},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def deleted_users(self, request):
        """Get all deleted users"""
        deleted_users = User.objects.filter(is_deleted=True)
        serializer = self.get_serializer(deleted_users, many=True)
        return Response(
            {
                "message": "Deleted users retrieved successfully",
                "users": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        """Restore a soft deleted user"""
        try:
            user = User.objects.get(pk=pk, is_deleted=True)
            user.is_deleted = False
            user.save()
            return Response(
                {
                    "message": "User restored successfully",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Deleted user not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["delete"])
    def permanent_delete(self, request, pk=None):
        """Permanently delete a user"""
        try:
            user = User.objects.get(pk=pk)
            user.delete()
            return Response(
                {"message": "User permanently deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


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


class SelfDetails(ListAPIView):
    queryset = User.objects.all()
    serializer_class = SelfAPISerilizer

    def list(self, request, *args, **kwargs):
        try:
            user = self.queryset.filter(id=request.user.id).first()
            if not user:
                return Response(
                    {"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.serializer_class(user, context={"request": request})
            data = serializer.data

            return Response(data)
        except Exception as e:
            traceback.print_exc()
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogoutView(APIView):
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        refresh_token = serializer.validated_data["refresh"]

        try:
            token = RefreshToken(refresh_token)
            try:
                token.blacklist()
                return Response(
                    {"detail": "Token blacklisted"},
                    status=status.HTTP_205_RESET_CONTENT,
                )
            except AttributeError:
                return Response(
                    {"detail": "Blacklisting not supported. Check your configuration."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except TokenError:
            return Response(
                {"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )