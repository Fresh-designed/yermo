import re
from urllib.parse import parse_qs, urlparse

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from . import b2

YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com"}
VIMEO_HOSTS = {"vimeo.com", "www.vimeo.com", "player.vimeo.com"}
YOUTUBE_ID = re.compile(r"^[\w-]{6,20}$")


class Course(models.Model):
    class Kind(models.TextChoices):
        VIDEO = "video", "Con videos"
        WRITTEN = "written", "Escrito"

    title = models.CharField("título", max_length=160)
    slug = models.SlugField("identificador", max_length=180, unique=True, blank=True)
    description = models.TextField("descripción", blank=True)
    kind = models.CharField("tipo", max_length=10, choices=Kind.choices, default=Kind.VIDEO)
    is_published = models.BooleanField("publicado", default=True)
    created_at = models.DateTimeField("creado", default=timezone.now, editable=False)

    class Meta:
        ordering = ["title"]
        verbose_name = "curso"
        verbose_name_plural = "cursos"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:180] or "curso"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("courses:detail", args=[self.slug])

    @property
    def is_written(self):
        return self.kind == self.Kind.WRITTEN


class Video(models.Model):
    """Una lección: un video, un texto o ambos.

    El video vive fuera (YouTube, Vimeo o un .mp4 público) y aquí se guarda su URL.
    El texto de una lección escrita se guarda en `content`.
    """

    course = models.ForeignKey(
        Course, verbose_name="curso", on_delete=models.CASCADE, related_name="videos"
    )
    title = models.CharField("título", max_length=160)
    url = models.URLField("URL del video", max_length=500, blank=True)
    content = models.TextField(
        "texto de la lección",
        blank=True,
        help_text="Separa los párrafos con una línea en blanco. «## » abre un subtítulo; "
        "«- » o «1. » al inicio de una línea crean una lista.",
    )
    order = models.PositiveIntegerField("orden", default=1)
    duration_minutes = models.PositiveIntegerField("duración (min)", null=True, blank=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "lección"
        verbose_name_plural = "lecciones"

    def __str__(self):
        return f"{self.course} · {self.order}. {self.title}"

    def clean(self):
        if not self.url and not self.content.strip():
            raise ValidationError("Una lección necesita la URL de un video, un texto o ambos.")

    @property
    def playback_url(self):
        """Dirección para el reproductor: un enlace temporal si el video está en el bucket de B2."""
        return b2.signed_url(self.url)

    @property
    def embed_url(self):
        """URL para un <iframe>, o None si es un archivo que va en un <video>."""
        parsed = urlparse(self.url)
        host = parsed.netloc.lower()
        segments = [s for s in parsed.path.split("/") if s]

        video_id = None
        if host == "youtu.be" and segments:
            video_id = segments[0]
        elif host in YOUTUBE_HOSTS:
            if segments[:1] in (["embed"], ["shorts"], ["live"]) and len(segments) > 1:
                video_id = segments[1]
            else:
                video_id = parse_qs(parsed.query).get("v", [None])[0]
        if video_id and YOUTUBE_ID.match(video_id):
            return f"https://www.youtube-nocookie.com/embed/{video_id}"

        if host in VIMEO_HOSTS and segments and segments[-1].isdigit():
            return f"https://player.vimeo.com/video/{segments[-1]}"
        return None


class Enrollment(models.Model):
    """Suscripción de un usuario a un curso."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="usuario",
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    course = models.ForeignKey(
        Course, verbose_name="curso", on_delete=models.CASCADE, related_name="enrollments"
    )
    created_at = models.DateTimeField("suscrito el", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "suscripción"
        verbose_name_plural = "suscripciones"
        constraints = [
            models.UniqueConstraint(fields=["user", "course"], name="unique_enrollment")
        ]

    def __str__(self):
        return f"{self.user} → {self.course}"


class WatchedVideo(models.Model):
    """Existe una fila por cada lección que un usuario ya vio o leyó."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="usuario",
        on_delete=models.CASCADE,
        related_name="watched_videos",
    )
    video = models.ForeignKey(
        Video, verbose_name="lección", on_delete=models.CASCADE, related_name="watched_by"
    )
    watched_at = models.DateTimeField("completada el", auto_now_add=True)

    class Meta:
        verbose_name = "lección completada"
        verbose_name_plural = "lecciones completadas"
        constraints = [
            models.UniqueConstraint(fields=["user", "video"], name="unique_watched_video")
        ]

    def __str__(self):
        return f"{self.user} vio {self.video}"


def progress_percent(watched, total):
    """Porcentaje entero de lecciones completadas. Un curso sin lecciones está en 0 %."""
    if not total:
        return 0
    return round(watched * 100 / total)
