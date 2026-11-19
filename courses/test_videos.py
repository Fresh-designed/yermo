import json
import shutil
import struct
import tempfile
from io import StringIO
from pathlib import Path
from unittest import mock
from urllib.parse import parse_qs, urlparse

from botocore.exceptions import ClientError
from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from . import b2
from .models import Course, Enrollment, Video
from .video_folder import clean_title, mp4_seconds, order_key, scan

User = get_user_model()

B2 = {
    "B2_KEY_ID": "004fakekeyid",
    "B2_APPLICATION_KEY": "K004fakeapplicationkey",
    "B2_BUCKET": "yermo-videos",
    "B2_ENDPOINT": "s3.us-east-005.backblazeb2.com",
}
NO_B2 = {key: "" for key in B2}
BUCKET_URL = "https://yermo-videos.s3.us-east-005.backblazeb2.com"


def box(kind, payload):
    return struct.pack(">I4s", 8 + len(payload), kind) + payload


def fake_mp4(seconds, timescale=1000, version=0, large=False):
    """MP4 mínimo: «ftyp», un «mdat» vacío y «moov» con su «mvhd» al final, como muchos videos."""
    if version == 1:
        mvhd = bytes([1, 0, 0, 0]) + bytes(16) + struct.pack(">IQ", timescale, int(seconds * timescale))
    else:
        mvhd = bytes(4) + bytes(8) + struct.pack(">II", timescale, int(seconds * timescale))
    mdat = box(b"mdat", bytes(32))
    if large:
        mdat = struct.pack(">I4sQ", 1, b"mdat", 16 + 32) + bytes(32)
    return box(b"ftyp", b"isom" + bytes(4)) + mdat + box(b"moov", box(b"mvhd", mvhd + bytes(80)))


class TitleTests(SimpleTestCase):
    def test_strips_numbers_and_separators(self):
        cases = {
            "02 Blender Settings": "Blender Settings",
            "10. Low poly chair": "Low poly chair",
            "01. 00 - Introduction to the tutorial": "Introduction to the tutorial",
            "11 Wind I  Animated Noise": "Wind I Animated Noise",
            "40. Material and Lighting Setup – Part 2": "Material and Lighting Setup – Part 2",
            "3D Modeling for Beginners": "3D Modeling for Beginners",
            "10 100 Tips": "100 Tips",
            "07": "07",
        }
        for name, expected in cases.items():
            self.assertEqual(clean_title(name), expected, name)

    def test_orders_by_number_then_name(self):
        names = ["10. c.mp4", "2. b.mp4", "intro.mp4", "1. a.mp4"]
        ordered = sorted((Path(name) for name in names), key=order_key)
        self.assertEqual([path.name for path in ordered], ["1. a.mp4", "2. b.mp4", "10. c.mp4", "intro.mp4"])


class DurationTests(SimpleTestCase):
    def setUp(self):
        self.folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.folder)

    def write(self, name, data):
        path = self.folder / name
        path.write_bytes(data)
        return path

    def test_reads_mvhd_versions_and_large_boxes(self):
        self.assertEqual(mp4_seconds(self.write("a.mp4", fake_mp4(90.5))), 90.5)
        self.assertEqual(mp4_seconds(self.write("b.mp4", fake_mp4(3725, version=1))), 3725)
        self.assertEqual(mp4_seconds(self.write("c.mp4", fake_mp4(12, large=True))), 12)

    def test_unreadable_files_return_none(self):
        self.assertIsNone(mp4_seconds(self.write("d.mp4", b"esto no es un video")))
        self.assertIsNone(mp4_seconds(self.write("e.mp4", b"")))
        self.assertIsNone(mp4_seconds(self.folder / "no-existe.mp4"))


class ScanTests(SimpleTestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        course = self.root / "Modelado 3D by Ana"
        course.mkdir()
        (course / "10. Final.mp4").write_bytes(fake_mp4(600))
        (course / "2. Inicio rápido.mp4").write_bytes(fake_mp4(65))
        (course / "notas.mov").write_bytes(b"x")
        (course / "descripcion.txt").write_text("Un curso de prueba.", encoding="utf-8")
        (self.root / "vacía").mkdir()
        (self.root / "suelto.mp4").write_bytes(fake_mp4(1))

    def test_builds_courses_lessons_and_keys(self):
        courses, skipped = scan(self.root)
        self.assertEqual(len(courses), 1)
        course = courses[0]
        self.assertEqual((course["title"], course["description"]), ("Modelado 3D by Ana", "Un curso de prueba."))
        lessons = course["lessons"]
        self.assertEqual([lesson["title"] for lesson in lessons], ["Inicio rápido", "Final"])
        self.assertEqual([lesson["seconds"] for lesson in lessons], [65, 600])
        self.assertEqual(
            [lesson["key"] for lesson in lessons],
            ["cursos/modelado-3d-by-ana/01-inicio-rapido.mp4", "cursos/modelado-3d-by-ana/02-final.mp4"],
        )
        reasons = {path.name: reason for path, reason in skipped}
        self.assertEqual(set(reasons), {"notas.mov", "vacía", "suelto.mp4"})


@override_settings(**B2)
class SignedUrlTests(SimpleTestCase):
    def test_builds_and_reads_bucket_urls(self):
        url = b2.public_url("cursos/curso/01-intro con espacio.mp4")
        self.assertEqual(url, f"{BUCKET_URL}/cursos/curso/01-intro%20con%20espacio.mp4")
        self.assertEqual(b2.key_from_url(url), "cursos/curso/01-intro con espacio.mp4")
        self.assertIsNone(b2.key_from_url("https://otro-bucket.s3.us-east-005.backblazeb2.com/x.mp4"))
        self.assertIsNone(b2.key_from_url("https://youtu.be/abcdefgh"))

    def test_signs_bucket_urls_for_six_hours(self):
        signed = b2.signed_url(f"{BUCKET_URL}/cursos/curso/01-intro.mp4")
        parsed = urlparse(signed)
        query = parse_qs(parsed.query)
        self.assertEqual(parsed.netloc, "yermo-videos.s3.us-east-005.backblazeb2.com")
        self.assertEqual(parsed.path, "/cursos/curso/01-intro.mp4")
        self.assertEqual(query["X-Amz-Expires"], ["21600"])
        self.assertIn("us-east-005", query["X-Amz-Credential"][0])
        self.assertIn("X-Amz-Signature", query)

    def test_other_urls_are_left_alone(self):
        for url in ("https://youtu.be/abcdefgh", "https://cdn.example.com/clase.mp4", ""):
            self.assertEqual(b2.signed_url(url), url)

    @override_settings(B2_BUCKET="yermo-videos-Hugo")
    def test_bucket_names_with_capitals_go_in_the_path(self):
        url = b2.public_url("cursos/curso/01-intro.mp4")
        self.assertEqual(url, "https://s3.us-east-005.backblazeb2.com/yermo-videos-Hugo/cursos/curso/01-intro.mp4")
        self.assertEqual(b2.key_from_url(url), "cursos/curso/01-intro.mp4")
        self.assertIsNone(b2.key_from_url("https://s3.us-east-005.backblazeb2.com/otro/cursos/x.mp4"))
        signed = urlparse(b2.signed_url(url))
        self.assertEqual(
            (signed.netloc, signed.path),
            ("s3.us-east-005.backblazeb2.com", "/yermo-videos-Hugo/cursos/curso/01-intro.mp4"),
        )
        self.assertIn("X-Amz-Signature", parse_qs(signed.query))

    @override_settings(B2_KEY_ID="", B2_APPLICATION_KEY="")
    def test_without_keys_the_url_is_returned_unsigned(self):
        url = f"{BUCKET_URL}/cursos/x.mp4"
        self.assertEqual(b2.signed_url(url), url)

    @override_settings(B2_ENDPOINT="backblaze.com")
    def test_wrong_endpoint_is_explained(self):
        with self.assertRaisesMessage(Exception, "B2_ENDPOINT"):
            b2.client()


@override_settings(**B2)
class PlayerTests(TestCase):
    def test_lesson_page_plays_a_signed_link(self):
        user = User.objects.create_user("nadia", "nadia@example.com", "x")
        course = Course.objects.create(title="Curso en B2")
        Video.objects.create(course=course, title="Intro", order=1, url=f"{BUCKET_URL}/cursos/curso/01-intro.mp4")
        Enrollment.objects.create(user=user, course=course)
        self.client.force_login(user)
        response = self.client.get(course.get_absolute_url())
        self.assertContains(response, '<video src="https://yermo-videos.s3.us-east-005.backblazeb2.com/cursos/curso/01-intro.mp4?')
        self.assertContains(response, "X-Amz-Signature=", count=2)


class FakeB2:
    """Imita las llamadas de boto3 que usan los comandos, sin conexión."""

    def __init__(self, stored=None, versions=None):
        self.stored = dict(stored or {})
        self.versions = list(versions or [])
        self.uploaded = []
        self.deleted = []

    def head_object(self, Bucket, Key):
        if Key not in self.stored:
            raise ClientError({"Error": {"Code": "404", "Message": "Not Found"}}, "HeadObject")
        return {"ContentLength": self.stored[Key]}

    def upload_file(self, filename, bucket, key, ExtraArgs):
        self.uploaded.append((Path(filename).name, bucket, key, ExtraArgs["ContentType"]))
        self.stored[key] = Path(filename).stat().st_size

    def get_paginator(self, name):
        assert name == "list_object_versions"
        versions = self.versions

        class Pages:
            def paginate(self, Bucket, Prefix):
                yield {"Versions": [item for item in versions if item["Key"].startswith(Prefix)]}

        return Pages()

    def delete_objects(self, Bucket, Delete):
        self.deleted.extend(Delete["Objects"])
        return {}


class UploadCommandTests(TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        course = self.root / "Blender Basics by Ana"
        course.mkdir()
        (course / "01 Interfaz.mp4").write_bytes(fake_mp4(125))
        (course / "02 Modelado.mp4").write_bytes(fake_mp4(30))
        self.output = self.root / "salida.json"

    def run_command(self, *args):
        out = StringIO()
        call_command("subir_videos", str(self.root), "--salida", str(self.output), *args, stdout=out)
        return out.getvalue()

    @override_settings(**NO_B2)
    def test_simulation_needs_no_keys_and_uploads_nothing(self):
        output = self.run_command("--simular")
        self.assertIn("Blender Basics by Ana: 2 lecciones", output)
        self.assertIn(" 1. Interfaz (2 min)", output)
        self.assertIn("no se subió nada", output)
        self.assertFalse(self.output.exists())

    @override_settings(**NO_B2)
    def test_upload_without_keys_explains_what_is_missing(self):
        with self.assertRaisesMessage(CommandError, "B2_KEY_ID"):
            self.run_command()

    @override_settings(**B2)
    def test_uploads_missing_files_and_writes_a_loadable_file(self):
        already = "cursos/blender-basics-by-ana/01-interfaz.mp4"
        fake = FakeB2(stored={already: (self.root / "Blender Basics by Ana" / "01 Interfaz.mp4").stat().st_size})
        with mock.patch("courses.b2.client", return_value=fake):
            output = self.run_command()
        self.assertIn("ya estaba subido", output)
        self.assertEqual(
            fake.uploaded,
            [("02 Modelado.mp4", "yermo-videos", "cursos/blender-basics-by-ana/02-modelado.mp4", "video/mp4")],
        )

        data = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual(data[0]["titulo"], "Blender Basics by Ana")
        self.assertEqual(data[0]["lecciones"][0], {"titulo": "Interfaz", "url": f"{BUCKET_URL}/{already}", "minutos": 2})

        call_command("cargar_cursos", str(self.output), stdout=StringIO())
        course = Course.objects.get()
        self.assertEqual(course.kind, Course.Kind.VIDEO)
        self.assertEqual([lesson.title for lesson in course.videos.all()], ["Interfaz", "Modelado"])
        self.assertEqual(course.videos.first().embed_url, None)


@override_settings(**B2)
class DeleteCommandTests(TestCase):
    def setUp(self):
        self.b2_course = Course.objects.create(title="Solo B2")
        Video.objects.create(course=self.b2_course, title="Uno", order=1, url=f"{BUCKET_URL}/cursos/solo-b2/01-uno.mp4")
        self.mixed = Course.objects.create(title="Mixto")
        Video.objects.create(course=self.mixed, title="YouTube", order=1, url="https://youtu.be/abcdefgh")
        Video.objects.create(course=self.mixed, title="B2", order=2, url=f"{BUCKET_URL}/cursos/mixto/02-b2.mp4")
        self.written = Course.objects.create(title="Escrito", kind=Course.Kind.WRITTEN)
        Video.objects.create(course=self.written, title="Texto", order=1, content="Hola")
        self.fake = FakeB2(
            versions=[
                {"Key": "cursos/solo-b2/01-uno.mp4", "VersionId": "v1", "Size": 100},
                {"Key": "cursos/solo-b2/01-uno.mp4", "VersionId": "v0", "Size": 90},
                {"Key": "cursos/mixto/02-b2.mp4", "VersionId": "v2", "Size": 50},
            ]
        )

    def run_command(self, *args):
        out = StringIO()
        with mock.patch("courses.b2.client", return_value=self.fake):
            call_command("borrar_videos", *args, stdout=out)
        return out.getvalue()

    def test_without_confirmation_nothing_is_deleted(self):
        output = self.run_command()
        self.assertIn("En B2: 3 archivos", output)
        self.assertIn("2 lecciones con video en B2, 1 cursos completos", output)
        self.assertEqual(self.fake.deleted, [])
        self.assertEqual(Video.objects.count(), 4)

    def test_confirmation_deletes_every_version_and_only_b2_content(self):
        self.run_command("--confirmar")
        self.assertEqual(len(self.fake.deleted), 3)
        self.assertEqual({item["VersionId"] for item in self.fake.deleted}, {"v0", "v1", "v2"})
        self.assertFalse(Course.objects.filter(pk=self.b2_course.pk).exists())
        self.assertEqual([lesson.title for lesson in self.mixed.videos.all()], ["YouTube"])
        self.assertTrue(self.written.videos.exists())

