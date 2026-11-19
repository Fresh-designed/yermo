from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import LoginForm, RegisterForm


class YermoLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get(self, request, *args, **kwargs):
        # Es el aviso de la portada: aparece al llegar sin sesión a una página protegida.
        if self.redirect_field_name in request.GET and not request.user.is_authenticated:
            messages.warning(request, "Inicia sesión para continuar.")
        return super().get(request, *args, **kwargs)


def register(request):
    if request.user.is_authenticated:
        return redirect("courses:my_courses")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        if user.is_staff:
            messages.success(request, f"Bienvenido, {user.username}. Tu cuenta es de administrador.")
        else:
            messages.success(request, f"Bienvenido al yermo, {user.username}.")
        next_url = request.POST.get("next", "")
        if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect("courses:catalog")
    return render(
        request,
        "accounts/register.html",
        {
            "form": form,
            "next": request.GET.get("next", request.POST.get("next", "")),
            "active_tab": "register",
        },
    )
