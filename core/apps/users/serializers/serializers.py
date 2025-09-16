from rest_framework import serializers
from core.apps.users.models import User, TrainerMember


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "role",
            "bio",
            "gender",
            "weight",
            "height",
            "age",
            "profile_image",
            "phone",
            "is_deleted",
        ]
        read_only_fields = ["id"]

    def validate_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain digits only.")
        if len(value) < 10:
            raise serializers.ValidationError(
                "Phone number must be at least 10 digits."
            )
        return value

    def validate_first_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("First name should contain only letters.")
        return value

    def validate_last_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("Last name should contain only letters.")
        return value

    def validate_email(self, value):
        # Skip validation during update if email hasn't changed
        if self.instance and self.instance.email == value:
            return value
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate_username(self, value):
        # Skip validation during update if username hasn't changed
        if self.instance and self.instance.username == value:
            return value
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_weight(self, value):
        if value is not None and (value <= 0 or value > 1000):
            raise serializers.ValidationError("Weight must be between 0 and 1000 kg.")
        return value

    def validate_height(self, value):
        if value is not None and (value <= 0 or value > 300):
            raise serializers.ValidationError("Height must be between 0 and 300 cm.")
        return value

    def validate_age(self, value):
        if value is not None and (value < 1 or value > 150):
            raise serializers.ValidationError("Age must be between 1 and 150.")
        return value


class TrainerMemberSerializer(serializers.ModelSerializer):
    trainer_name = serializers.CharField(source="trainer.username", read_only=True)
    member_name = serializers.CharField(source="member.username", read_only=True)

    class Meta:
        model = TrainerMember
        fields = [
            "id",
            "trainer",
            "trainer_name",
            "member",
            "member_name",
            "assigned_date",
            "is_active",
            "notes",
            "is_deleted",
        ]
        read_only_fields = ["assigned_date"]

    def validate(self, data):
        if data["trainer"] == data["member"]:
            raise serializers.ValidationError(
                "Trainer and member cannot be the same person"
            )

        # Check if trainer has role 'trainer'
        if data["trainer"].role != "trainer":
            raise serializers.ValidationError("Selected user is not a trainer")

        # Check if member has role 'member'
        if data["member"].role != "member":
            raise serializers.ValidationError("Selected user is not a member")

        return data
