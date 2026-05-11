"""Business logic for the posts app.

All mutations of ``Post`` go through here so the API layer remains thin
and side effects (slug generation, excerpt fallback, publish timestamping)
live in one place.
"""
from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.core.utils import build_excerpt, unique_slug

from .models import Post, PostStatus


def _resolve_excerpt(*, excerpt: str | None, content: str) -> str:
    if excerpt:
        return excerpt.strip()
    return build_excerpt(content)


@transaction.atomic
def create_post(*, author, title: str, content: str, **extra: Any) -> Post:
    status = extra.pop("status", PostStatus.DRAFT)
    excerpt = _resolve_excerpt(excerpt=extra.pop("excerpt", None), content=content)
    slug = extra.pop("slug", None) or unique_slug(Post, title)

    published_at = None
    if status == PostStatus.PUBLISHED:
        published_at = extra.pop("published_at", None) or timezone.now()

    return Post.objects.create(
        author=author,
        title=title,
        slug=slug,
        content=content,
        excerpt=excerpt,
        status=status,
        published_at=published_at,
        **extra,
    )


@transaction.atomic
def update_post(post: Post, **fields: Any) -> Post:
    """Apply a partial update. Recomputes excerpt and publish stamp when needed."""
    dirty: list[str] = []

    for key in ("title", "content", "slug", "cover_image"):
        if key in fields and fields[key] is not None:
            setattr(post, key, fields[key])
            dirty.append(key)

    if "excerpt" in fields:
        post.excerpt = _resolve_excerpt(
            excerpt=fields.get("excerpt"),
            content=fields.get("content", post.content),
        )
        dirty.append("excerpt")
    elif "content" in fields and not post.excerpt:
        post.excerpt = build_excerpt(post.content)
        dirty.append("excerpt")

    if "status" in fields and fields["status"] is not None:
        new_status = fields["status"]
        if new_status != post.status:
            post.status = new_status
            dirty.append("status")
            if new_status == PostStatus.PUBLISHED and post.published_at is None:
                post.published_at = timezone.now()
                dirty.append("published_at")

    if dirty:
        post.save(update_fields=list(dict.fromkeys(dirty)))
    return post


@transaction.atomic
def delete_post(post: Post) -> None:
    post.delete()


def publish_post(post: Post) -> Post:
    return update_post(post, status=PostStatus.PUBLISHED)


def archive_post(post: Post) -> Post:
    return update_post(post, status=PostStatus.ARCHIVED)
