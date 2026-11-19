from django.contrib import admin
from django.db import models
from django.db.models import Count
from django.forms import Textarea

from .models import Course, Enrollment, Video, WatchedVideo


class VideoInline(admin.StackedInline):
    model = Video
    extra = 1
    fields = (("order", "title", "duration_minutes"), "url", "content")
    formfield_overrides = {models.TextField: {"widget": Textarea(attrs={"rows": 8, "cols": 90})}}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "video_count", "is_published", "created_at")
    list_filter = ("kind", "is_published")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [VideoInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_video_count=Count("videos"))

    @admin.display(description="lecciones", ordering="_video_count")
    def video_count(self, obj):
        return obj._video_count


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order", "duration_minutes")
    list_filter = ("course__kind", "course")
    search_fields = ("title",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "created_at")
    list_filter = ("course",)


@admin.register(WatchedVideo)
class WatchedVideoAdmin(admin.ModelAdmin):
    list_display = ("user", "video", "watched_at")
    list_filter = ("video__course",)
