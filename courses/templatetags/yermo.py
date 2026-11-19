import re

from django import template
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

register = template.Library()

ORDERED_ITEM = re.compile(r"^\d+\.\s+")


@register.filter
def lessons_label(course, count):
    """«8 videos» en un curso con videos; «3 lecciones» en uno escrito."""
    if course.is_written:
        word = "lección" if count == 1 else "lecciones"
    else:
        word = "video" if count == 1 else "videos"
    return f"{count} {word}"


@register.filter
def done_label(course, count):
    """«3 vistos» en un curso con videos; «2 leídas» en uno escrito."""
    if course.is_written:
        word = "leída" if count == 1 else "leídas"
    else:
        word = "visto" if count == 1 else "vistos"
    return f"{count} {word}"


@register.filter
def lesson_text(value):
    """Texto de una lección como HTML: párrafos, «## » subtítulos y listas con «- » o «1. ».

    Todo lo que escribe el autor se escapa; solo salen las etiquetas que se arman aquí.
    """
    blocks, paragraph, items = [], [], []
    list_tag = "ul"

    def flush_paragraph():
        if paragraph:
            lines = format_html_join(mark_safe("<br>"), "{}", ((line,) for line in paragraph))
            blocks.append(format_html("<p>{}</p>", lines))
            paragraph.clear()

    def flush_items():
        if items:
            rows = format_html_join("", "<li>{}</li>", ((item,) for item in items))
            blocks.append(format_html("<{}>{}</{}>", list_tag, rows, list_tag))
            items.clear()

    for raw in str(value).splitlines():
        line = raw.strip()
        ordered = ORDERED_ITEM.match(line)
        if line.startswith("- ") or ordered:
            flush_paragraph()
            tag = "ol" if ordered else "ul"
            if tag != list_tag:
                flush_items()
                list_tag = tag
            items.append(line[ordered.end():] if ordered else line[2:])
            continue
        flush_items()
        if line.startswith("## "):
            flush_paragraph()
            blocks.append(format_html("<h3>{}</h3>", line[3:]))
        elif line:
            paragraph.append(line)
        else:
            flush_paragraph()
    flush_paragraph()
    flush_items()
    return mark_safe("".join(blocks))
