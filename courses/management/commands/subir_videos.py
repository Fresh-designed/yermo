import json
import time
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError

from courses import b2
from courses.video_folder import minutes, scan

MB = 1024 * 1024


def _size(byte_count):
    return f"{byte_count / (1024 * MB):.2f} GB" if byte_count >= 1024 * MB else f"{byte_count / MB:.0f} MB"


def _duration(seconds):
    hours, rest = divmod(round(seconds), 3600)
    return f"{hours} h {rest // 60:02d} min" if hours else f"{rest // 60} min"


class Command(BaseCommand):
    help = (
        "Sube a Backblaze B2 los videos de una carpeta (una subcarpeta por curso) y escribe un "
        "archivo para `cargar_cursos`. Con --simular solo muestra lo que haría."
    )

    def add_arguments(self, parser):
        parser.add_argument("carpeta", help="Carpeta con una subcarpeta por curso")
        parser.add_argument(
            "--simular", action="store_true", help="Muestra cursos y lecciones sin subir nada"
        )
        parser.add_argument(
            "--salida", default="cursos-videos.json", help="Archivo para cargar_cursos (por defecto cursos-videos.json)"
        )

    def handle(self, *args, **options):
        try:
            courses, skipped = scan(options["carpeta"])
        except FileNotFoundError:
            raise CommandError(f"No existe la carpeta «{options['carpeta']}».")
        if not courses:
            raise CommandError("No encontré ningún curso: hace falta una subcarpeta por curso con videos dentro.")

        self._summary(courses, skipped)
        if options["simular"]:
            self.stdout.write("Simulación: no se subió nada.")
            return

        try:
            client = b2.client()
        except ImproperlyConfigured as error:
            raise CommandError(str(error))

        total = sum(len(course["lessons"]) for course in courses)
        done = 0
        for course in courses:
            for lesson in course["lessons"]:
                done += 1
                self._upload(client, settings.B2_BUCKET, lesson, f"[{done}/{total}]")

        output = Path(options["salida"])
        output.write_text(json.dumps(self._as_data(courses), ensure_ascii=False, indent=2), encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Videos en B2: {total}. Cursos guardados en {output}."))
        self.stdout.write(f"Siguiente paso: python manage.py cargar_cursos {output}")

    def _summary(self, courses, skipped):
        for course in courses:
            lessons = course["lessons"]
            size = sum(lesson["size"] for lesson in lessons)
            seconds = sum(lesson["seconds"] or 0 for lesson in lessons)
            self.stdout.write(
                f"• {course['title']}: {len(lessons)} lecciones, {_size(size)}, {_duration(seconds)}"
            )
            for number, lesson in enumerate(lessons, start=1):
                length = f"{minutes(lesson['seconds'])} min" if lesson["seconds"] else "duración desconocida"
                self.stdout.write(f"    {number:2d}. {lesson['title']} ({length})")
        total = sum(lesson["size"] for course in courses for lesson in course["lessons"])
        self.stdout.write(f"Total: {len(courses)} cursos, {_size(total)}.")
        for path, reason in skipped:
            self.stdout.write(self.style.WARNING(f"Omitido «{path.name}»: {reason}."))

    def _upload(self, client, bucket, lesson, counter):
        from botocore.exceptions import BotoCoreError, ClientError

        name = lesson["path"].name
        try:
            existing = client.head_object(Bucket=bucket, Key=lesson["key"])
            if existing["ContentLength"] == lesson["size"]:
                self.stdout.write(f"{counter} {name}: ya estaba subido.")
                return
        except ClientError as error:
            code = error.response.get("Error", {}).get("Code")
            if code not in ("404", "NoSuchKey", "NotFound"):
                raise CommandError(self._explain(error)) from error

        started = time.monotonic()
        self.stdout.write(f"{counter} {name}: subiendo {_size(lesson['size'])}…")
        try:
            client.upload_file(
                str(lesson["path"]),
                bucket,
                lesson["key"],
                ExtraArgs={"ContentType": lesson["content_type"]},
            )
        except (ClientError, BotoCoreError) as error:
            raise CommandError(
                f"{self._explain(error)} Vuelve a ejecutar el comando: los videos ya subidos se saltan."
            ) from error
        self.stdout.write(f"{counter} {name}: listo en {round(time.monotonic() - started)} s.")

    @staticmethod
    def _explain(error):
        code = getattr(error, "response", {}).get("Error", {}).get("Code", "")
        if code in ("403", "AccessDenied", "InvalidAccessKeyId", "SignatureDoesNotMatch"):
            return (
                "Backblaze rechazó la clave. Revisa B2_KEY_ID, B2_APPLICATION_KEY y B2_ENDPOINT en .env, "
                "y que la clave tenga permiso de lectura y escritura sobre el bucket."
            )
        if code in ("NoSuchBucket", "AllAccessDisabled"):
            return "Ese bucket no existe en tu cuenta. Revisa B2_BUCKET en .env."
        return f"Backblaze respondió con un error: {error}."

    @staticmethod
    def _as_data(courses):
        return [
            {
                "titulo": course["title"],
                "descripcion": course["description"],
                "tipo": "video",
                "lecciones": [
                    {
                        "titulo": lesson["title"],
                        "url": b2.public_url(lesson["key"]),
                        **({"minutos": minutes(lesson["seconds"])} if lesson["seconds"] else {}),
                    }
                    for lesson in course["lessons"]
                ],
            }
            for course in courses
        ]
