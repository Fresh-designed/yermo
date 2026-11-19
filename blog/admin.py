from django.contrib import admin
from django.utils.text import Truncator

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("author", "created_at", "excerpt", "with_photo")
    list_filter = ("courses",)
    search_fields = ("author__username", "body")
    filter_horizontal = ("courses",)
    date_hierarchy = "created_at"

    def get_queryset(self, request):
        # La foto puede pesar cientos de KB: no hace falta para listar ni editar.
        return super().get_queryset(request).defer("image")

    @admin.display(description="mensaje")
    def excerpt(self, obj):
        return Truncator(obj.body).chars(80)

    @admin.display(description="con foto", boolean=True)
    def with_photo(self, obj):
        return obj.has_image
