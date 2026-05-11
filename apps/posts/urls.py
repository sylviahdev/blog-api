"""URL routes for the posts app — wired via a DRF router."""
from rest_framework.routers import DefaultRouter

from .views import PostViewSet

app_name = "posts"

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")

urlpatterns = router.urls
