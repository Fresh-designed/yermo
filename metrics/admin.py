from django.contrib import admin

from .models import ActivityEvent


@admin.register(ActivityEvent)
class ActivityEventAdmin(admin.ModelAdmin):
    list_display = ("created_at", "kind", "username")
    list_filter = ("kind",)
    search_fields = ("username",)
    date_hierarchy = "created_at"
