from django.core.management.base import BaseCommand

from courses.loader import create_courses
from courses.written_courses import WRITTEN_COURSES


class Command(BaseCommand):
    help = (
        "Crea los cursos escritos de Yermo que todavía no existan. "
        "No modifica ni duplica los que ya están en la base de datos."
    )

    def handle(self, *args, **options):
        created, existing = create_courses(WRITTEN_COURSES)
        self.stdout.write(
            self.style.SUCCESS(f"Cursos escritos creados: {created}. Ya existían: {existing}.")
        )
