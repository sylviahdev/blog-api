"""Serializers for the posts app. Strictly validation + projection."""
from __future__ import annotations

from rest_framework import serializers

from apps.users.serializers import UserPublicSerializer

from .models import Post, PostStatus


class PostListSerializer(serializers.ModelSerializer):
    """Compact representation for list endpoints — omits full content."""

    author = UserPublicSerializer(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "slug",
            "excerpt",
            "cover_image",
            "status",
            "author",
            "published_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class PostDetailSerializer(serializers.ModelSerializer):
    """Full representation for retrieve / create / update responses."""

    author = UserPublicSerializer(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "slug",
            "excerpt",
            "cover_image",
            "content",
            "status",
            "author",
            "published_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "slug",
            "author",
            "published_at",
            "created_at",
            "updated_at",
        )


class PostWriteSerializer(serializers.ModelSerializer):
    """Input-only serializer enforcing the create/update contract."""

    status = serializers.ChoiceField(choices=PostStatus.choices, required=False)

    class Meta:
        model = Post
        fields = ("title", "content", "excerpt", "cover_image", "status")
        extra_kwargs = {
            "title": {"required": True, "allow_blank": False},
            "content": {"required": True, "allow_blank": False},
            "excerpt": {"required": False, "allow_blank": True},
            "cover_image": {"required": False, "allow_blank": True},
        }

    def validate_title(self, value: str) -> str:
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters.")
        return value
