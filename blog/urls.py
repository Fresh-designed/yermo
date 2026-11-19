from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.feed, name="feed"),
    path("foto/<int:post_id>/", views.photo, name="photo"),
    path("publicacion/<int:post_id>/eliminar/", views.delete_post, name="delete_post"),
]
