"""DRF serializers for the users app. Validation only — no business logic."""
from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserPublicSerializer(serializers.ModelSerializer):
    """Read-only projection safe to embed in other resources (e.g. posts)."""

    class Meta:
        model = User
        fields = ("id", "username", "full_name")
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    """Full self-profile representation."""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "full_name",
            "bio",
            "is_staff",
            "date_joined",
        )
        read_only_fields = ("id", "email", "is_staff", "date_joined")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, max_length=128)

    class Meta:
        model = User
        fields = ("email", "username", "password", "full_name")
        extra_kwargs = {
            "email": {"required": True},
            "username": {"required": True},
            "full_name": {"required": False, "allow_blank": True},
        }

    def validate_email(self, value: str) -> str:
        value = value.lower().strip()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value: str) -> str:
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is taken.")
        return value


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "full_name", "bio")
        extra_kwargs = {
            "username": {"required": False},
            "full_name": {"required": False, "allow_blank": True},
            "bio": {"required": False, "allow_blank": True},
        }

    def validate_username(self, value: str) -> str:
        qs = User.objects.filter(username__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("This username is taken.")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8, max_length=128)
