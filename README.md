# blog-api-backend

Production-grade Django REST Framework backend for a blog system.

## Stack

- Django 5 + Django REST Framework
- PostgreSQL
- SimpleJWT for authentication
- python-dotenv for environment configuration
- django-filter, django-cors-headers

## Architecture

```
config/         Django project (settings, urls, wsgi, asgi)
apps/
  core/         Shared base models, permissions, helpers
  users/        Custom user model, JWT auth, profile
  posts/        Blog CRUD with service layer
api/v1/         Versioned URL layer (single mount point)
common/         Cross-app helpers (pagination, response envelope, mixins)
```

Design rules:

- **Thin views**. Mutations live in `services.py`; views just translate HTTP <-> services.
- **Serializers validate**, services act, models persist.
- **Permissions are reusable** (`apps/core/permissions.py`).
- **URL versioning** under `/api/v1/` so v2 is additive, not a rewrite.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # then edit values
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Endpoints

All endpoints are prefixed with `/api/v1/`.

| Method | Path                          | Auth        | Purpose                           |
|--------|-------------------------------|-------------|-----------------------------------|
| GET    | `/health/`                    | public      | Healthcheck                       |
| POST   | `/auth/register/`             | public      | Create an account                 |
| POST   | `/auth/login/`                | public      | Obtain JWT access + refresh       |
| POST   | `/auth/token/refresh/`        | refresh tok | Rotate the access token           |
| POST   | `/auth/token/verify/`         | public      | Verify a token                    |
| GET    | `/auth/me/`                   | bearer      | Get current profile               |
| PATCH  | `/auth/me/`                   | bearer      | Update current profile            |
| POST   | `/auth/password/`             | bearer      | Change password                   |
| GET    | `/posts/`                     | public      | List published posts              |
| POST   | `/posts/`                     | bearer      | Create a post                     |
| GET    | `/posts/{slug}/`              | public      | Retrieve a post                   |
| PATCH  | `/posts/{slug}/`              | author      | Partial update                    |
| PUT    | `/posts/{slug}/`              | author      | Full update                       |
| DELETE | `/posts/{slug}/`              | author      | Delete                            |
| POST   | `/posts/{slug}/publish/`      | author      | Transition draft → published      |
| POST   | `/posts/{slug}/archive/`      | author      | Transition published → archived   |

## Authentication

Standard JWT bearer tokens. Send `Authorization: Bearer <access>` on requests.
Refresh tokens are rotated and blacklisted after rotation (see `SIMPLE_JWT`
settings).

## Error envelope

Errors are returned in a consistent shape:

```json
{
  "error": {
    "status": 400,
    "code": "validation_error",
    "message": "Invalid input.",
    "details": { "title": ["This field is required."] }
  }
}
```

## Production notes

- Configure `DJANGO_DEBUG=False` and a real `DJANGO_SECRET_KEY`.
- Set `DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`.
- Serve behind TLS — `SECURE_SSL_REDIRECT` and HSTS are flipped on automatically when `DEBUG=False`.
- Run with `gunicorn config.wsgi:application` (or `daphne config.asgi:application` if you need async).
