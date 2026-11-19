from django.conf import settings
from django.db import models
from django.utils import timezone


class ActivityEvent(models.Model):
    """Registro del flujo de usuarios. Sobrevive al borrado de la cuenta que lo generó."""

    class Kind(models.TextChoices):
        VISIT = "visit", "Visita diaria"
        LOGIN = "login", "Inicio de sesión"
        REGISTER = "register", "Registro"
        DELETE = "delete", "Eliminación"

    kind = models.CharField("tipo", max_length=10, choices=Kind.choices)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_events",
    )
    username = models.CharField("nombre de usuario", max_length=150)
    created_at = models.DateTimeField("fecha", default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "evento de actividad"
        verbose_name_plural = "eventos de actividad"

    def __str__(self):
        return f"{self.get_kind_display()}: {self.username}"

    @classmethod
    def record(cls, kind, user):
        return cls.objects.create(kind=kind, user=user, username=user.get_username())
