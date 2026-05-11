from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "published_at", "created_at")
    list_filter = ("status", "created_at", "published_at")
    search_fields = ("title", "excerpt", "content", "author__email", "author__username")
    autocomplete_fields = ("author",)
    readonly_fields = ("id", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    fieldsets = (
        (None, {"fields": ("title", "slug", "author", "status")}),
        ("Content", {"fields": ("excerpt", "content")}),
        ("Timestamps", {"fields": ("published_at", "created_at", "updated_at")}),
    )
