from io import StringIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import CommandError, call_command
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .loader import CourseDataError, create_courses
from .models import Course, Enrollment, Video, WatchedVideo, progress_percent
from .templatetags.yermo import lesson_text

User = get_user_model()


class ProgressPercentTests(SimpleTestCase):
    def test_values(self):
        self.assertEqual(progress_percent(0, 4), 0)
        self.assertEqual(progress_percent(1, 3), 33)
        self.assertEqual(progress_percent(4, 4), 100)
        self.assertEqual(progress_percent(0, 0), 0)


class EmbedUrlTests(SimpleTestCase):
    def test_providers(self):
        cases = {
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=3": "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ": "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ": "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ",
            "https://vimeo.com/76979871": "https://player.vimeo.com/video/76979871",
            "https://cdn.example.com/clase.mp4": None,
            "": None,
        }
        for url, expected in cases.items():
            self.assertEqual(Video(url=url).embed_url, expected, url)


class LessonTextTests(SimpleTestCase):
    def test_blocks(self):
        html = lesson_text("uno\ndos\n\n## Título\n1. a\n2. b\n- c")
        self.assertEqual(
            html,
            "<p>uno<br>dos</p><h3>Título</h3><ol><li>a</li><li>b</li></ol><ul><li>c</li></ul>",
        )

    def test_escapes_html(self):
        html = lesson_text("<script>alert(1)</script>\n- <b>x</b>\n## <i>y</i>")
        self.assertNotIn("<script>", html)
        self.assertNotIn("<b>", html)
        self.assertNotIn("<i>", html)
        self.assertIn("&lt;script&gt;", html)


class CourseFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("nadia", "nadia@example.com", "x")
        self.other = User.objects.create_user("omar", "omar@example.com", "x")
        self.course = Course.objects.create(title="Cartografía básica")
        self.videos = [
            Video.objects.create(course=self.course, title=f"Clase {n}", order=n, url=f"https://youtu.be/video{n}xx")
            for n in range(1, 5)
        ]
        self.client.force_login(self.user)

    def enroll(self):
        return self.client.post(reverse("courses:enroll", args=[self.course.slug]))

    def mark(self, video, watched="1"):
        return self.client.post(reverse("courses:set_watched", args=[video.pk]), {"watched": watched})

    def test_pages_require_login(self):
        self.client.logout()
        for url in (reverse("courses:catalog"), reverse("courses:my_courses"), self.course.get_absolute_url()):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn("/cuenta/entrar/", response.url)

    def test_video_url_is_hidden_until_enrolled(self):
        self.assertNotContains(self.client.get(self.course.get_absolute_url()), "<iframe")
        self.enroll()
        self.assertContains(self.client.get(self.course.get_absolute_url()), "<iframe")

    def test_watch_url_redirects_when_not_enrolled(self):
        url = reverse("courses:watch", args=[self.course.slug, self.videos[0].pk])
        self.assertRedirects(self.client.get(url), self.course.get_absolute_url())

    def test_my_courses_shows_percent_and_counts(self):
        self.enroll()
        self.mark(self.videos[0])
        response = self.client.get(reverse("courses:my_courses"))
        enrollment = response.context["enrollments"][0]
        self.assertEqual(enrollment.video_total, 4)
        self.assertEqual(enrollment.video_watched, 1)
        self.assertEqual(enrollment.percent, 25)
        self.assertContains(response, "25%")
        self.assertContains(response, "4 videos en total · 1 visto")

    def test_progress_is_per_user(self):
        self.enroll()
        Enrollment.objects.create(user=self.other, course=self.course)
        for video in self.videos[:3]:
            WatchedVideo.objects.create(user=self.other, video=video)
        response = self.client.get(reverse("courses:my_courses"))
        self.assertEqual(response.context["enrollments"][0].percent, 0)

    def test_marking_twice_counts_once_and_can_be_undone(self):
        self.enroll()
        self.mark(self.videos[0])
        self.mark(self.videos[0])
        self.assertEqual(WatchedVideo.objects.filter(user=self.user).count(), 1)
        self.mark(self.videos[0], watched="0")
        self.assertFalse(WatchedVideo.objects.filter(user=self.user).exists())

    def test_cannot_mark_without_enrollment(self):
        self.mark(self.videos[0])
        self.assertFalse(WatchedVideo.objects.exists())

    def test_state_changes_reject_get(self):
        self.assertEqual(self.client.get(reverse("courses:enroll", args=[self.course.slug])).status_code, 405)
        self.assertEqual(self.client.get(reverse("courses:set_watched", args=[self.videos[0].pk])).status_code, 405)

    def test_unpublished_course_is_hidden(self):
        self.enroll()
        Course.objects.filter(pk=self.course.pk).update(is_published=False)
        self.assertEqual(self.client.get(self.course.get_absolute_url()).status_code, 404)
        self.assertEqual(len(self.client.get(reverse("courses:my_courses")).context["enrollments"]), 0)


class WrittenCourseTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("nadia", "nadia@example.com", "x")
        self.written = Course.objects.create(title="Tips de dibujo", kind=Course.Kind.WRITTEN)
        self.lesson = Video.objects.create(
            course=self.written, title="El trazo", order=1, content="Suelta la mano.\n\n## Paso\n- uno"
        )
        self.with_video = Course.objects.create(title="Blender en video")
        Video.objects.create(course=self.with_video, title="Intro", order=1, url="https://youtu.be/abcdefgh")
        self.client.force_login(self.user)

    def catalog(self, **params):
        return self.client.get(reverse("courses:catalog"), params)

    def test_catalog_filters_by_kind(self):
        self.assertEqual(len(self.catalog().context["courses"]), 2)
        self.assertEqual(list(self.catalog(tipo="escrito").context["courses"]), [self.written])
        self.assertEqual(list(self.catalog(tipo="video").context["courses"]), [self.with_video])
        self.assertEqual(len(self.catalog(tipo="otro").context["courses"]), 2)

    def test_catalog_labels_each_kind(self):
        response = self.catalog()
        self.assertContains(response, "1 lección")
        self.assertContains(response, "1 video")
        self.assertContains(response, "Escrito")
        self.assertContains(response, "Con videos")

    def test_written_lesson_shows_text_instead_of_player(self):
        self.client.post(reverse("courses:enroll", args=[self.written.slug]))
        response = self.client.get(self.written.get_absolute_url())
        self.assertContains(response, "<p>Suelta la mano.</p><h3>Paso</h3><ul><li>uno</li></ul>")
        self.assertContains(response, "Marcar como leída")
        self.assertNotContains(response, "<iframe")
        self.assertNotContains(response, "<video")

    def test_my_courses_counts_read_lessons(self):
        self.client.post(reverse("courses:enroll", args=[self.written.slug]))
        self.client.post(reverse("courses:set_watched", args=[self.lesson.pk]), {"watched": "1"})
        response = self.client.get(reverse("courses:my_courses"))
        self.assertContains(response, "1 lección en total · 1 leída")
        self.assertEqual(response.context["enrollments"][0].percent, 100)

    def test_lesson_needs_a_video_or_a_text(self):
        with self.assertRaises(ValidationError):
            Video(course=self.written, title="Vacía", order=2).full_clean()
        Video(course=self.written, title="Con texto", order=2, content="Hola").full_clean()


class SeedCommandTests(TestCase):
    def run_command(self):
        output = StringIO()
        call_command("cargar_cursos_escritos", stdout=output)
        return output.getvalue()

    def test_creates_ten_written_courses_with_valid_lessons(self):
        self.assertIn("creados: 10", self.run_command())
        courses = Course.objects.filter(kind=Course.Kind.WRITTEN)
        self.assertEqual(courses.count(), 10)
        self.assertEqual(Video.objects.count(), 30)
        for lesson in Video.objects.all():
            lesson.full_clean()
            self.assertEqual(lesson.url, "")
            self.assertIn("## Ejercicio", lesson.content)

    def test_second_run_keeps_edits_and_adds_nothing(self):
        self.run_command()
        course = Course.objects.first()
        course.title = "Título cambiado por el administrador"
        course.save()
        self.assertIn("creados: 0", self.run_command())
        self.assertEqual(Course.objects.count(), 10)
        course.refresh_from_db()
        self.assertEqual(course.title, "Título cambiado por el administrador")


class LoaderTests(TestCase):
    VIDEO_COURSE = {
        "titulo": "Modelado 3D en video",
        "descripcion": "Clase a clase.",
        "lecciones": [
            {"titulo": "Introducción", "url": "https://youtu.be/abcdefgh", "minutos": 10},
            {"titulo": "Lectura de apoyo", "texto": "Un párrafo."},
        ],
    }

    def test_creates_courses_in_order_and_defaults_to_video(self):
        self.assertEqual(create_courses([self.VIDEO_COURSE]), (1, 0))
        course = Course.objects.get()
        self.assertEqual((course.slug, course.kind), ("modelado-3d-en-video", Course.Kind.VIDEO))
        lessons = list(course.videos.values_list("order", "title", "duration_minutes"))
        self.assertEqual(lessons, [(1, "Introducción", 10), (2, "Lectura de apoyo", None)])

    def test_existing_courses_are_left_alone(self):
        create_courses([self.VIDEO_COURSE])
        Course.objects.update(description="Editado en el panel.")
        other = {"titulo": "Otro curso", "tipo": "escrito", "lecciones": [{"titulo": "Uno", "texto": "Hola"}]}
        self.assertEqual(create_courses([self.VIDEO_COURSE, other]), (1, 1))
        self.assertEqual(Course.objects.get(slug="modelado-3d-en-video").description, "Editado en el panel.")
        self.assertEqual(Video.objects.count(), 3)

    def test_invalid_data_saves_nothing_and_says_where(self):
        cases = {
            "lección 2": [self.VIDEO_COURSE, {"titulo": "Roto", "lecciones": [{"titulo": "Ok", "texto": "x"}, {"titulo": "Vacía"}]}],
            "Curso 1 (sin título)": [{"descripcion": "Sin título"}],
            '"tipo"': [{"titulo": "Raro", "tipo": "audio"}],
            "URL": [{"titulo": "Mala URL", "lecciones": [{"titulo": "x", "url": "no es una url"}]}],
            "lista de cursos": {"titulo": "No es una lista"},
        }
        for expected, data in cases.items():
            with self.assertRaises(CourseDataError) as caught:
                create_courses(data)
            self.assertIn(expected, str(caught.exception))
            self.assertFalse(Course.objects.exists(), expected)

    def test_example_file_loads_with_the_command(self):
        output = StringIO()
        call_command("cargar_cursos", str(settings.BASE_DIR / "cursos.ejemplo.json"), stdout=output)
        self.assertIn("Cursos creados: 2. Ya existían: 0.", output.getvalue())
        self.assertEqual(Video.objects.filter(course__kind=Course.Kind.VIDEO).count(), 3)

    def test_command_explains_a_missing_or_broken_file(self):
        with self.assertRaisesMessage(CommandError, "No existe el archivo"):
            call_command("cargar_cursos", "no-existe.json")
        broken = settings.BASE_DIR / "prueba-rota.json"
        broken.write_text('[{"titulo": "Falta cerrar"', encoding="utf-8")
        try:
            with self.assertRaisesMessage(CommandError, "no es JSON válido"):
                call_command("cargar_cursos", str(broken))
        finally:
            broken.unlink()
