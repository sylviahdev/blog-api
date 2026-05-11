"""Project-wide utility helpers."""
from __future__ import annotations

import re
import unicodedata

from django.utils.text import slugify as django_slugify


def unique_slug(model, value: str, *, field: str = "slug", max_length: int = 255) -> str:
    """Generate a slug that does not collide with existing rows.

    Appends an incrementing numeric suffix when a collision is found.
    The slug is truncated to ``max_length`` (including suffix).
    """
    base = django_slugify(value) or "untitled"
    base = base[:max_length]
    candidate = base
    suffix = 2
    qs = model._default_manager.filter(**{field: candidate})
    while qs.exists():
        suffix_str = f"-{suffix}"
        candidate = f"{base[: max_length - len(suffix_str)]}{suffix_str}"
        qs = model._default_manager.filter(**{field: candidate})
        suffix += 1
    return candidate


_WHITESPACE_RE = re.compile(r"\s+")


def build_excerpt(text: str, *, max_length: int = 200) -> str:
    """Collapse whitespace and truncate text to a single-line excerpt."""
    normalized = unicodedata.normalize("NFKC", text or "").strip()
    collapsed = _WHITESPACE_RE.sub(" ", normalized)
    if len(collapsed) <= max_length:
        return collapsed
    return collapsed[: max_length - 1].rstrip() + "…"
