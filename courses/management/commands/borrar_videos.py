from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses import b2
from courses.models import Course, Video

PREFIX = "cursos/"


class Command(BaseCommand):
    help = (
        "Borra de Backblaze B2 los videos que subió `subir_videos` y, de la base de datos, "
        "las lecciones y cursos que los usaban. Sin --confirmar solo muestra lo que borraría."
    )

    def add_arguments(self, parser):
        parser.add_argument("--confirmar", action="store_true", help="Borra de verdad")

    def handle(self, *args, **options):
        lessons = [lesson for lesson in Video.objects.select_related("course") if b2.key_from_url(lesson.url)]
        courses = {lesson.course for lesson in lessons}
        whole_courses = [
            course for course in courses if all(b2.key_from_url(item.url) for item in course.videos.all())
        ]

        versions = []
        if b2.is_configured():
            try:
                versions = self._bucket_versions()
            except ImproperlyConfigured as error:
                raise CommandError(str(error))
        else:
            self.stdout.write(self.style.WARNING("Sin datos de B2 en .env: solo se revisa la base de datos."))

        stored = sum(version.get("Size", 0) for version in versions)
        self.stdout.write(f"En B2: {len(versions)} archivos, {stored / 1024 ** 3:.2f} GB.")
        self.stdout.write(
            f"En la base de datos: {len(lessons)} lecciones con video en B2, "
            f"{len(whole_courses)} cursos completos."
        )
        for course in sorted(whole_courses, key=lambda item: item.title):
            self.stdout.write(f"    • {course.title}")

        if not options["confirmar"]:
            self.stdout.write("No se borró nada. Para borrarlo, repite el comando con --confirmar.")
            return

        if versions:
            self._delete_versions(versions)
        with transaction.atomic():
            # Al borrar un curso se borran también sus suscripciones y el avance de sus lecciones.
            Course.objects.filter(pk__in=[course.pk for course in whole_courses]).delete()
            Video.objects.filter(pk__in=[lesson.pk for lesson in lessons]).delete()
        self.stdout.write(self.style.SUCCESS("Listo: videos y cursos borrados."))

    def _bucket_versions(self):
        """Todas las versiones de los archivos bajo «cursos/». B2 guarda versiones antiguas y también ocupan."""
        client = b2.client()
        pages = client.get_paginator("list_object_versions").paginate(Bucket=settings.B2_BUCKET, Prefix=PREFIX)
        versions = []
        for page in pages:
            versions.extend(page.get("Versions", []))
            versions.extend(page.get("DeleteMarkers", []))
        return versions

    def _delete_versions(self, versions):
        client = b2.client()
        for start in range(0, len(versions), 1000):
            batch = versions[start : start + 1000]
            response = client.delete_objects(
                Bucket=settings.B2_BUCKET,
                Delete={
                    "Objects": [{"Key": item["Key"], "VersionId": item["VersionId"]} for item in batch],
                    "Quiet": True,
                },
            )
            if response.get("Errors"):
                first = response["Errors"][0]
                raise CommandError(
                    f"B2 no pudo borrar {len(response['Errors'])} archivos, por ejemplo «{first.get('Key')}»: "
                    f"{first.get('Message', first.get('Code'))}. No se tocó la base de datos."
                )
