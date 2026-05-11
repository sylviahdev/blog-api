"""Abstract base models shared across the project."""
from __future__ import annotations

import uuid

from django.db import models


class TimeStampedModel(models.Model):
    """Adds self-managed `created_at` / `updated_at` timestamps."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ("-created_at",)


class UUIDModel(models.Model):
    """Uses a UUID primary key — safer for public-facing identifiers."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimeStampedModel):
    """Default base: UUID PK + audit timestamps. Inherit from this in apps."""

    class Meta:
        abstract = True
        ordering = ("-created_at",)
