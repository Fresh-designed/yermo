from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import PERSONAL_FIELDS, SurveyForm
from .models import SurveyResponse

# Qué significan los extremos de la escala en cada pregunta.
SCALE_HINTS = {
    "overall": "1 = Nada satisfecho · 5 = Muy satisfecho",
    "content": "1 = Muy mala · 5 = Excelente",
    "ease": "1 = Muy difícil · 5 = Muy fácil",
}


@login_required
def survey(request):
    response = SurveyResponse.objects.filter(user=request.user).first()
    form = SurveyForm(request.POST or None, instance=response)
    if request.method == "POST" and form.is_valid():
        SurveyResponse.objects.update_or_create(user=request.user, defaults=form.cleaned_data)
        messages.success(request, "Gracias. Guardamos tu respuesta.")
        return redirect("surveys:survey")
    return render(
        request,
        "surveys/survey.html",
        {
            "form": form,
            "person_fields": [form[name] for name in PERSONAL_FIELDS],
            "scales": [(form[name], hint) for name, hint in SCALE_HINTS.items()],
            "response": response,
        },
    )
