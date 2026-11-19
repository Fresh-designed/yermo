"""Crea cursos y lecciones a partir de datos sencillos.

Lo usan `cargar_cursos` (un archivo JSON tuyo) y `cargar_cursos_escritos` (los cursos
que trae Yermo). Formato de cada curso:

    {
      "titulo": "Modelado 3D en video",
      "descripcion": "Texto corto para el catálogo.",
      "tipo": "video",                      # "video" (por defecto) o "escrito"
      "lecciones": [
        {"titulo": "Introducción", "url": "https://youtu.be/…", "minutos": 10},
        {"titulo": "Lectura", "texto": "Párrafo…"}
      ]
    }
"""
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.text import slugify

from .models import Course, Video

KINDS = {"video": Course.Kind.VIDEO, "escrito": Course.Kind.WRITTEN}


class CourseDataError(ValueError):
    """Un dato no se puede guardar. El mensaje dice en qué curso o lección y por qué."""


def _validate(instance, where):
    try:
        instance.full_clean()
    except ValidationError as error:
        raise CourseDataError(f"{where}: {' '.join(error.messages)}") from error


@transaction.atomic
def create_courses(items):
    """Crea los cursos de `items` que todavía no existan. Devuelve `(creados, existentes)`.

    Un curso ya existe si otro tiene la misma dirección, que sale de su título.
    Si algún dato no es válido lanza `CourseDataError` y no se guarda nada.
    """
    if not isinstance(items, list):
        raise CourseDataError("Los datos deben ser una lista de cursos: [ {…}, {…} ].")

    created = existing = 0
    for number, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise CourseDataError(f"Curso {number}: debe ir entre llaves, {{ … }}.")
        title = str(item.get("titulo", "")).strip()
        where = f"Curso {number} ({title or 'sin título'})"
        kind = KINDS.get(item.get("tipo", "video"))
        if kind is None:
            raise CourseDataError(f'{where}: "tipo" debe ser "video" o "escrito".')
        lessons = item.get("lecciones", [])
        if not isinstance(lessons, list) or not all(isinstance(lesson, dict) for lesson in lessons):
            raise CourseDataError(f'{where}: "lecciones" debe ser una lista de lecciones, [ {{…}}, {{…}} ].')

        slug = slugify(title)[:180]
        if slug and Course.objects.filter(slug=slug).exists():
            existing += 1
            continue

        course = Course(title=title, slug=slug, description=item.get("descripcion", ""), kind=kind)
        _validate(course, where)
        course.save()
        for order, data in enumerate(lessons, start=1):
            lesson = Video(
                course=course,
                order=order,
                title=str(data.get("titulo", "")).strip(),
                url=data.get("url", ""),
                content=str(data.get("texto", "")).strip(),
                duration_minutes=data.get("minutos"),
            )
            _validate(lesson, f"{where}, lección {order}")
            lesson.save()
        created += 1
    return created, existing
