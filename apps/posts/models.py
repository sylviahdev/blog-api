"""Post model: the central blog entity."""
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel


class PostStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    PUBLISHED = "published", _("Published")
    ARCHIVED = "archived", _("Archived")


class PublishedPostManager(models.Manager):
    """Default-ordering manager scoped to publicly visible posts."""

    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(status=PostStatus.PUBLISHED)


class Post(BaseModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    excerpt = models.CharField(max_length=300, blank=True)
    content = models.TextField()
    status = models.CharField(
        max_length=16,
        choices=PostStatus.choices,
        default=PostStatus.DRAFT,
        db_index=True,
    )
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )

    objects = models.Manager()
    published = PublishedPostManager()

    class Meta:
        ordering = ("-published_at", "-created_at")
        indexes = [
            models.Index(fields=("status", "-published_at")),
            models.Index(fields=("author", "-created_at")),
        ]

    def __str__(self) -> str:
        return self.title

    @property
    def is_published(self) -> bool:
        return self.status == PostStatus.PUBLISHED
