from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

SCALE = [(value, str(value)) for value in range(1, 6)]
MIN_AGE, MAX_AGE = 10, 100


class SurveyResponse(models.Model):
    """Respuesta de un usuario a la encuesta de satisfacción. Hay una por usuario y puede cambiarla."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="usuario",
        on_delete=models.CASCADE,
        related_name="survey_response",
    )
    # Pueden quedar vacíos en la base para no invalidar respuestas anteriores; el formulario los exige.
    full_name = models.CharField("nombre", max_length=120, blank=True)
    age = models.PositiveSmallIntegerField(
        "edad",
        null=True,
        blank=True,
        validators=[MinValueValidator(MIN_AGE), MaxValueValidator(MAX_AGE)],
    )
    career = models.CharField("carrera", max_length=120, blank=True)
    overall =models.PositiveSmallIntegerField("satisfacción general", choices=SCALE)
    content = models.PositiveSmallIntegerField("calidad de los cursos", choices=SCALE)
    ease = models.PositiveSmallIntegerField("facilidad de uso", choices=SCALE)
    recommend = models.BooleanField("recomendaría Yermo")
    comment = models.TextField("comentario", blank=True, max_length=1000)
    created_at = models.DateTimeField("respondida el", auto_now_add=True)
    updated_at = models.DateTimeField("actualizada el", auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "respuesta de la encuesta"
        verbose_name_plural = "respuestas de la encuesta"

    def __str__(self):
        return f"{self.user}: {self.overall}/5"
