"""Filter set for the Post resource.

Exposes ergonomic query params layered on top of the underlying model:

    ?published=true       -- only published posts
    ?published=false      -- everything except published (drafts + archived)
    ?status=draft         -- exact status match
    ?author=alice         -- case-insensitive username match
"""
from __future__ import annotations

import django_filters

from .models import Post, PostStatus


class PostFilterSet(django_filters.FilterSet):
    published = django_filters.BooleanFilter(method="filter_published")
    author = django_filters.CharFilter(field_name="author__username", lookup_expr="iexact")
    status = django_filters.ChoiceFilter(choices=PostStatus.choices)
    created_after = django_filters.IsoDateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.IsoDateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Post
        fields = ("status", "author", "published", "created_after", "created_before")

    def filter_published(self, queryset, name, value):
        if value is True:
            return queryset.filter(status=PostStatus.PUBLISHED)
        if value is False:
            return queryset.exclude(status=PostStatus.PUBLISHED)
        return queryset
