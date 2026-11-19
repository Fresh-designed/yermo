from django.contrib import admin
from django.urls import include, path

from courses.views import home

urlpatterns = [
    path("", home, name="home"),
    path("cuenta/", include("accounts.urls")),
    path("cursos/", include("courses.urls")),
    path("blog/", include("blog.urls")),
    path("encuesta/", include("surveys.urls")),
    path("metricas/", include("metrics.urls")),
    path("admin/", admin.site.urls),
]
