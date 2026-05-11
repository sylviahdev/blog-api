"""Reusable view / serializer mixins."""
from __future__ import annotations

from typing import ClassVar


class MultiSerializerMixin:
    """Pick a serializer per DRF action via a ``serializer_classes`` mapping.

    Example::

        class PostViewSet(MultiSerializerMixin, viewsets.ModelViewSet):
            serializer_class = PostDetailSerializer
            serializer_classes = {
                "list": PostListSerializer,
                "create": PostWriteSerializer,
                "update": PostWriteSerializer,
                "partial_update": PostWriteSerializer,
            }
    """

    serializer_classes: ClassVar[dict[str, type]] = {}

    def get_serializer_class(self):
        if self.serializer_classes:
            cls = self.serializer_classes.get(self.action)
            if cls is not None:
                return cls
        return super().get_serializer_class()


class InjectRequestUserMixin:
    """Inject ``request.user`` into serializer.save() as the given field name."""

    user_field: ClassVar[str] = "author"

    def perform_create(self, serializer):
        serializer.save(**{self.user_field: self.request.user})
