from django.urls import path

from . import views

app_name = "metrics"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("usuarios/<int:user_id>/eliminar/", views.delete_user, name="delete_user"),
]
