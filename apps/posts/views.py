"""ViewSet for the Post resource — controllers stay thin, services do the work."""
from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from apps.core.permissions import IsAuthorOrAdmin

from . import services
from .models import Post, PostStatus
from .serializers import (
    PostDetailSerializer,
    PostListSerializer,
    PostWriteSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    """CRUD for blog posts.

    * Anonymous users: read published posts only.
    * Authenticated users: write their own posts; read their own drafts.
    * Staff: full visibility & write access.
    """

    queryset = Post.objects.select_related("author").all()
    lookup_field = "slug"
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrAdmin)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ("status", "author__username")
    search_fields = ("title", "excerpt", "content")
    ordering_fields = ("published_at", "created_at", "updated_at", "title")
    ordering = ("-published_at", "-created_at")

    # -- Querying ----------------------------------------------------------
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return qs
        if user.is_authenticated:
            return qs.filter(models_q_self_or_published(user))
        return qs.filter(status=PostStatus.PUBLISHED)

    # -- Serializer selection ---------------------------------------------
    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action in {"create", "update", "partial_update"}:
            return PostWriteSerializer
        return PostDetailSerializer

    # -- Write actions delegate to services -------------------------------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = services.create_post(author=request.user, **serializer.validated_data)
        return Response(
            PostDetailSerializer(post).data, status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        post = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        post = services.update_post(post, **serializer.validated_data)
        return Response(PostDetailSerializer(post).data)

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        services.delete_post(post)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # -- Custom actions ----------------------------------------------------
    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, slug=None):
        post = services.publish_post(self.get_object())
        return Response(PostDetailSerializer(post).data)

    @action(detail=True, methods=["post"], url_path="archive")
    def archive(self, request, slug=None):
        post = services.archive_post(self.get_object())
        return Response(PostDetailSerializer(post).data)


# Local helper to keep the viewset readable. Defined at module scope so it can
# be unit-tested independently and so the queryset method stays one-liner-ish.
def models_q_self_or_published(user):
    from django.db.models import Q

    return Q(status=PostStatus.PUBLISHED) | Q(author=user)
