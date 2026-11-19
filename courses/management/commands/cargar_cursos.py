import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from courses.loader import CourseDataError, create_courses


class Command(BaseCommand):
    help = (
        "Crea cursos y lecciones a partir de un archivo JSON (mira cursos.ejemplo.json). "
        "No modifica ni duplica los cursos que ya existen."
    )

    def add_arguments(self, parser):
        parser.add_argument("archivo", help="Ruta del archivo, por ejemplo cursos.json")

    def handle(self, *args, **options):
        path = Path(options["archivo"])
        try:
            # utf-8-sig acepta el archivo con o sin la marca BOM que añaden algunos editores.
            items = json.loads(path.read_text(encoding="utf-8-sig"))
        except FileNotFoundError:
            raise CommandError(f"No existe el archivo «{path}» en esta carpeta.")
        except UnicodeDecodeError:
            raise CommandError("El archivo no está en UTF-8. Guárdalo de nuevo con esa codificación.")
        except json.JSONDecodeError as error:
            raise CommandError(
                f"El archivo no es JSON válido. Revisa la línea {error.lineno}, columna {error.colno}: "
                "suele faltar o sobrar una coma, unas comillas o una llave."
            )
        try:
            created, existing = create_courses(items)
        except CourseDataError as error:
            raise CommandError(f"{error} No se guardó ningún curso.")
        self.stdout.write(self.style.SUCCESS(f"Cursos creados: {created}. Ya existían: {existing}."))
