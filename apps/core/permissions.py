"""Reusable DRF permission classes."""
from __future__ import annotations

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Object-level permission: only the owner of an object can mutate it.

    Reads are unconditionally allowed. Mutations require the object's
    ``author`` (or ``owner`` / ``user``) field to match ``request.user``.
    """

    owner_fields = ("author", "owner", "user")

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        owner = self._resolve_owner(obj)
        return owner is not None and owner == request.user

    def _resolve_owner(self, obj):
        for field in self.owner_fields:
            if hasattr(obj, field):
                return getattr(obj, field)
        return None


class IsAdminOrReadOnly(permissions.BasePermission):
    """Anyone may read; only staff users may write."""

    def has_permission(self, request, view) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsAuthorOrAdmin(permissions.BasePermission):
    """Mutation requires staff status OR being the resource's author."""

    def has_permission(self, request, view) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.is_staff:
            return True
        author = getattr(obj, "author", None)
        return author == request.user
