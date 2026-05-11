"""Standard API response shape and exception handler.

Successful list / detail endpoints return the resource payload directly
(or the paginator's envelope), so clients can rely on DRF conventions.

Errors are normalised into a consistent envelope:

    {
        "error": {
            "status": 400,
            "code": "validation_error",
            "message": "Invalid input.",
            "details": { ... }
        }
    }
"""
from __future__ import annotations

from typing import Any

from rest_framework import status as http_status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def success(data: Any = None, *, status: int = http_status.HTTP_200_OK) -> Response:
    """Build a successful response. Useful for ad-hoc endpoints."""
    return Response(data, status=status)


def error(
    message: str,
    *,
    code: str = "error",
    status: int = http_status.HTTP_400_BAD_REQUEST,
    details: Any = None,
) -> Response:
    payload: dict[str, Any] = {
        "error": {
            "status": status,
            "code": code,
            "message": message,
        }
    }
    if details is not None:
        payload["error"]["details"] = details
    return Response(payload, status=status)


def api_exception_handler(exc, context):
    """Wraps DRF's default handler in the standard error envelope."""
    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    code = "error"
    message = "An error occurred."
    details: Any = None

    if isinstance(exc, APIException):
        code = exc.default_code or code
        message = str(exc.detail) if not isinstance(exc.detail, (list, dict)) else exc.default_detail
        if isinstance(exc.detail, (list, dict)):
            details = exc.detail

    response.data = {
        "error": {
            "status": response.status_code,
            "code": code,
            "message": message,
            **({"details": details} if details is not None else {}),
        }
    }
    return response
