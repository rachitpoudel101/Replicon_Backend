from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.apps.membership.models import Membership
from datetime import date

User = get_user_model()


class MembershipSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source="member.username", read_only=True)
    member_email = serializers.CharField(source="member.email", read_only=True)

    class Meta:
        model = Membership
        fields = [
            "id",
            "member",
            "member_name",
            "member_email",
            "plan_type",
            "start_date",
            "end_date",
            "is_active",
        ]

    def validate(self, data):
        if "start_date" in data and "end_date" in data:
            if data["end_date"] <= data["start_date"]:
                raise serializers.ValidationError("End date must be after start date")
        return data

    def validate_start_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("Start date cannot be in the past")
        return value

    def validate_member(self, value):
        if value.role != "member":
            raise serializers.ValidationError("Selected user is not a member")
        return value
