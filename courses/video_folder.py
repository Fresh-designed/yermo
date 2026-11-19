"""Lee una carpeta de videos y la convierte en cursos y lecciones.

Estructura esperada: una subcarpeta por curso y, dentro, un video por lección. El orden
sale del número con que empieza cada archivo («2. Intro.mp4» va antes que «10. Final.mp4»).
"""
import os
import re
import struct
from math import inf
from pathlib import Path

from django.utils.text import slugify

VIDEO_TYPES = {".mp4": "video/mp4", ".m4v": "video/mp4", ".webm": "video/webm"}
DESCRIPTION_FILE = "descripcion.txt"

# «02 Ajustes», «10. Silla», «3 - Luz»: número inicial con su separador.
FIRST_PREFIX = re.compile(r"^\s*\d+\s*(?:[.)_\-–—]+\s*|\s+)")
# Un segundo número solo se quita si lleva signo detrás («01. 00 - Intro»), para no comerse «100 Tips».
SECOND_PREFIX = re.compile(r"^\s*\d+\s*[.)_\-–—]+\s*")
LEADING_NUMBER = re.compile(r"^\s*(\d+)")


def clean_title(name):
    """«01. 00 - Introducción» → «Introducción»."""
    title = name
    for pattern in (FIRST_PREFIX, SECOND_PREFIX):
        stripped = pattern.sub("", title, count=1)
        if stripped.strip():
            title = stripped
    return " ".join(title.split()) or name.strip()


def order_key(path):
    match = LEADING_NUMBER.match(path.stem)
    return (int(match.group(1)) if match else inf, path.name.lower())


def mp4_seconds(path):
    """Duración en segundos de un MP4, M4V o MOV, leída de su caja «mvhd». None si no se encuentra."""
    try:
        with open(path, "rb") as handle:
            size = os.fstat(handle.fileno()).st_size
            for kind, start, end in _boxes(handle, 0, size):
                if kind == b"moov":
                    return _mvhd_seconds(handle, start, end)
    except (OSError, struct.error, IndexError):
        return None
    return None


def _boxes(handle, start, end):
    """Recorre las cajas de un archivo MP4 entre `start` y `end`: (tipo, inicio del contenido, fin)."""
    position = start
    while position + 8 <= end:
        handle.seek(position)
        size, kind = struct.unpack(">I4s", handle.read(8))
        header = 8
        if size == 1:
            size = struct.unpack(">Q", handle.read(8))[0]
            header = 16
        elif size == 0:
            size = end - position
        if size < header:
            return
        yield kind, position + header, min(position + size, end)
        position += size


def _mvhd_seconds(handle, start, end):
    for kind, body, _ in _boxes(handle, start, end):
        if kind != b"mvhd":
            continue
        handle.seek(body)
        version = handle.read(4)[0]
        if version == 1:
            handle.seek(16, os.SEEK_CUR)
            timescale, duration = struct.unpack(">IQ", handle.read(12))
        else:
            handle.seek(8, os.SEEK_CUR)
            timescale, duration = struct.unpack(">II", handle.read(8))
        return duration / timescale if timescale else None
    return None


def scan(folder):
    """Devuelve `(cursos, omitidos)`. Cada curso es un dict con sus lecciones en orden."""
    folder = Path(folder)
    if not folder.is_dir():
        raise FileNotFoundError(folder)

    courses, skipped = [], []
    for entry in sorted(folder.iterdir(), key=lambda path: path.name.lower()):
        if entry.is_file():
            skipped.append((entry, "está fuera de una carpeta de curso"))
            continue
        title = clean_title(entry.name)
        slug = slugify(title)[:120] or "curso"
        description_file = entry / DESCRIPTION_FILE
        lessons = []
        files = sorted(
            (path for path in entry.rglob("*") if path.is_file() and path.name != DESCRIPTION_FILE),
            key=lambda path: ([part.lower() for part in path.relative_to(entry).parts[:-1]], order_key(path)),
        )
        for path in files:
            suffix = path.suffix.lower()
            if suffix not in VIDEO_TYPES:
                skipped.append((path, "no es MP4, M4V ni WebM"))
                continue
            number = len(lessons) + 1
            lesson_title = clean_title(path.stem)
            lessons.append(
                {
                    "path": path,
                    "title": lesson_title,
                    "size": path.stat().st_size,
                    "seconds": mp4_seconds(path) if suffix != ".webm" else None,
                    "content_type": VIDEO_TYPES[suffix],
                    "key": f"cursos/{slug}/{number:02d}-{slugify(lesson_title)[:80] or 'leccion'}{suffix}",
                }
            )
        if not lessons:
            skipped.append((entry, "no contiene videos"))
            continue
        courses.append(
            {
                "title": title,
                "description": (
                    description_file.read_text(encoding="utf-8-sig").strip()
                    if description_file.is_file()
                    else ""
                ),
                "lessons": lessons,
            }
        )
    return courses, skipped


def minutes(seconds):
    return max(1, round(seconds / 60)) if seconds else None
