from django import forms

from .models import MAX_AGE, MIN_AGE, SCALE, SurveyResponse

PERSONAL_FIELDS = ("full_name", "age", "career")


class SurveyForm(forms.ModelForm):
    overall = forms.TypedChoiceField(
        label="¿Qué tan satisfecho estás con Yermo en general?",
        choices=SCALE,
        coerce=int,
        widget=forms.RadioSelect,
    )
    content = forms.TypedChoiceField(
        label="¿Cómo valoras la calidad de los cursos?",
        choices=SCALE,
        coerce=int,
        widget=forms.RadioSelect,
    )
    ease = forms.TypedChoiceField(
        label="¿Qué tan fácil te resulta usar la página?",
        choices=SCALE,
        coerce=int,
        widget=forms.RadioSelect,
    )
    recommend = forms.TypedChoiceField(
        label="¿Recomendarías Yermo a otra persona?",
        choices=[("si", "Sí"), ("no", "No")],
        coerce=lambda value: value == "si",
        widget=forms.RadioSelect,
    )

    class Meta:
        model = SurveyResponse
        fields = (*PERSONAL_FIELDS, "overall", "content", "ease", "recommend", "comment")
        labels = {
            "full_name": "Nombre completo",
            "age": "Edad",
            "career": "Carrera",
            "comment": "¿Qué mejorarías? (opcional)",
        }
        widgets = {
            "full_name": forms.TextInput(attrs={"autocomplete": "name"}),
            "age": forms.NumberInput(attrs={"min": MIN_AGE, "max": MAX_AGE, "inputmode": "numeric"}),
            "career": forms.TextInput(attrs={"placeholder": "Por ejemplo, Diseño gráfico"}),
            "comment": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in PERSONAL_FIELDS:
            self.fields[name].required = True
        if self.instance.pk:
            self.initial["recommend"] = "si" if self.instance.recommend else "no"

    def clean_full_name(self):
        return " ".join(self.cleaned_data["full_name"].split())

    def clean_career(self):
        return " ".join(self.cleaned_data["career"].split())
