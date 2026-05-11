"""Thin API views — all mutations delegate to ``apps.users.services``."""
from __future__ import annotations

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .serializers import (
    ChangePasswordSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    UserSerializer,
)


@extend_schema(
    tags=["auth"],
    summary="Register a new user",
    responses={201: UserSerializer},
)
class RegisterView(generics.CreateAPIView):
    """POST /auth/register/ — public."""

    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = services.register_user(**serializer.validated_data)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["auth"], summary="Retrieve or update the current user")
class MeView(generics.RetrieveUpdateAPIView):
    """GET / PATCH /auth/me/ — authenticated user's profile."""

    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        serializer = ProfileUpdateSerializer(
            instance=request.user, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        user = services.update_profile(request.user, **serializer.validated_data)
        return Response(UserSerializer(user).data)


class ChangePasswordView(APIView):
    """POST /auth/password/ — rotate the authenticated user's password."""

    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["auth"],
        summary="Change the current user's password",
        request=ChangePasswordSerializer,
        responses={204: OpenApiResponse(description="Password changed")},
    )
    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.change_password(
            request.user,
            current=serializer.validated_data["current_password"],
            new=serializer.validated_data["new_password"],
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
