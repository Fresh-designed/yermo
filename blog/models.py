from django.conf import settings
from django.db import models
from django.utils import timezone


class Post(models.Model):
    """Publicación del blog: un mensaje, una foto o ambos, con cursos etiquetados.

    La foto se guarda dentro de la base de datos porque el disco de Render gratuito
    se borra en cada reinicio. Siempre es un JPEG ya reducido (ver `blog/images.py`).
    """

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="autor",
        on_delete=models.CASCADE,
        related_name="posts",
    )
    body = models.TextField("mensaje", blank=True, max_length=2000)
    image = models.BinaryField("foto", null=True, blank=True, editable=False)
    image_width = models.PositiveIntegerField(null=True, blank=True, editable=False)
    image_height = models.PositiveIntegerField(null=True, blank=True, editable=False)
    courses = models.ManyToManyField(
        "courses.Course", verbose_name="cursos etiquetados", blank=True, related_name="posts"
    )
    created_at = models.DateTimeField("publicado", default=timezone.now, editable=False, db_index=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "publicación"
        verbose_name_plural = "publicaciones"

    def __str__(self):
        return f"{self.author} · {self.created_at:%d/%m/%Y %H:%M}"

    @property
    def has_image(self):
        return self.image_width is not None
