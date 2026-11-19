from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("entrar/", views.YermoLoginView.as_view(), name="login"),
    path("registro/", views.register, name="register"),
    path("salir/", LogoutView.as_view(), name="logout"),
]
