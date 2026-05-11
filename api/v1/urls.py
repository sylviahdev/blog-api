"""API v1 router — the single mount point for every versioned endpoint.

When v2 ships, add ``api/v2/urls.py`` and mount it in ``config/urls.py``
alongside this module. Apps stay version-agnostic; only this file changes.
"""
from django.http import JsonResponse
from django.urls import include, path
from django.views.decorators.http import require_GET
from drf_spectacular.utils import extend_schema

app_name = "v1"


@extend_schema(tags=["system"], summary="Healthcheck", responses={200: dict})
@require_GET
def healthcheck(_request):
    return JsonResponse({"status": "ok", "version": "v1"})


urlpatterns = [
    path("health/", healthcheck, name="health"),
    path("auth/", include("apps.users.urls", namespace="users")),
    path("", include("apps.posts.urls", namespace="posts")),
]
