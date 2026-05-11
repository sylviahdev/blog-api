"""Business logic for the users app.

Views should treat these functions as the single seam for user mutations.
This keeps controllers thin and lets us swap implementations (e.g. add
welcome-email side effects) without touching the API layer.
"""
from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework.exceptions import ValidationError as DRFValidationError

User = get_user_model()


def _to_drf_error(exc: DjangoValidationError) -> DRFValidationError:
    return DRFValidationError({"password": list(exc.messages)})


@transaction.atomic
def register_user(
    *,
    email: str,
    username: str,
    password: str,
    full_name: str = "",
    **extra: Any,
) -> "User":
    """Create a new user account after validating the password policy."""
    try:
        validate_password(password)
    except DjangoValidationError as exc:
        raise _to_drf_error(exc) from exc

    return User.objects.create_user(
        email=email,
        username=username,
        password=password,
        full_name=full_name,
        **extra,
    )


@transaction.atomic
def update_profile(user: "User", **fields: Any) -> "User":
    """Patch a user's mutable profile fields."""
    allowed = {"username", "full_name", "bio"}
    changed = []
    for key, value in fields.items():
        if key not in allowed or value is None:
            continue
        setattr(user, key, value)
        changed.append(key)
    if changed:
        user.save(update_fields=changed)
    return user


@transaction.atomic
def change_password(user: "User", *, current: str, new: str) -> None:
    if not user.check_password(current):
        raise DRFValidationError({"current_password": ["Wrong password."]})
    try:
        validate_password(new, user=user)
    except DjangoValidationError as exc:
        raise _to_drf_error(exc) from exc
    user.set_password(new)
    user.save(update_fields=["password"])
