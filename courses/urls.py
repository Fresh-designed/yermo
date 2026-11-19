from django.urls import path

from . import views

app_name = "courses"

urlpatterns = [
    path("", views.catalog, name="catalog"),
    path("mis-cursos/", views.my_courses, name="my_courses"),
    path("video/<int:video_id>/visto/", views.set_watched, name="set_watched"),
    path("<slug:slug>/", views.detail, name="detail"),
    path("<slug:slug>/video/<int:video_id>/", views.detail, name="watch"),
    path("<slug:slug>/suscribirse/", views.enroll, name="enroll"),
    path("<slug:slug>/cancelar/", views.unenroll, name="unenroll"),
]
