"""Resumen de la encuesta para el panel de métricas."""
from django.db.models import Avg, Count, Q
from django.db.models.functions import Lower

from courses.models import progress_percent

from .models import SurveyResponse

OVERALL_LABELS = {
    5: "Muy satisfecho",
    4: "Satisfecho",
    3: "Neutral",
    2: "Poco satisfecho",
    1: "Nada satisfecho",
}
CAREER_ROWS = 6


def survey_summary():
    totals = SurveyResponse.objects.aggregate(
        total=Count("id"),
        overall=Avg("overall"),
        content=Avg("content"),
        ease=Avg("ease"),
        recommend=Count("id", filter=Q(recommend=True)),
        age=Avg("age"),
    )
    total = totals["total"]
    counts = dict(
        SurveyResponse.objects.values_list("overall").annotate(count=Count("id")).order_by()
    )
    peak = max(counts.values(), default=0)
    # «Diseño» y «diseño» cuentan como la misma carrera.
    careers = list(
        SurveyResponse.objects.exclude(career="")
        .annotate(key=Lower("career"))
        .values("key")
        .annotate(count=Count("id"))
        .order_by("-count", "key")[:CAREER_ROWS]
    )
    career_peak = careers[0]["count"] if careers else 0
    return {
        "total": total,
        "averages": [
            {"label": "Satisfacción general", "value": totals["overall"]},
            {"label": "Calidad de los cursos", "value": totals["content"]},
            {"label": "Facilidad de uso", "value": totals["ease"]},
        ],
        "recommend_percent": progress_percent(totals["recommend"], total),
        "age": totals["age"],
        "careers": [
            {
                "label": row["key"][:1].upper() + row["key"][1:],
                "count": row["count"],
                "width": progress_percent(row["count"], career_peak),
            }
            for row in careers
        ],
        "distribution": [
            {
                "score": score,
                "label": label,
                "count": counts.get(score, 0),
                # Ancho de la barra respecto a la opción más votada.
                "width": progress_percent(counts.get(score, 0), peak),
            }
            for score, label in OVERALL_LABELS.items()
        ],
        "comments": SurveyResponse.objects.exclude(comment="").select_related("user")[:5],
    }
