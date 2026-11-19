from django.contrib import admin

from .models import SurveyResponse


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ("full_name", "age", "career", "user", "overall", "content", "ease", "recommend", "updated_at")
    list_filter = ("overall", "recommend", "career")
    search_fields = ("full_name", "career", "user__username", "comment")
