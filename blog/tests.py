from io import BytesIO
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from courses.models import Course

from .models import Post

User = get_user_model()


def png(size=(40, 30), mode="RGB", color=(200, 30, 30)):
    buffer = BytesIO()
    Image.new(mode, size, color).save(buffer, "PNG")
    return SimpleUploadedFile("foto.png", buffer.getvalue(), "image/png")


def noisy_png():
    """Un PNG que no se comprime casi nada: pesa varias decenas de KB."""
    buffer = BytesIO()
    Image.effect_noise((200, 200), 80).save(buffer, "PNG")
    return SimpleUploadedFile("ruido.png", buffer.getvalue(), "image/png")


class BlogTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user("nadia", "nadia@example.com", "x")
        self.other = User.objects.create_user("omar", "omar@example.com", "x")
        self.admin = User.objects.create_user("ada", "ada@example.com", "x", is_staff=True)
        self.course = Course.objects.create(title="Tips de dibujo")
        self.hidden = Course.objects.create(title="Curso oculto", is_published=False)
        self.url = reverse("blog:feed")
        self.client.force_login(self.author)

    def post(self, **data):
        return self.client.post(self.url, data)

    def test_requires_login(self):
        self.client.logout()
        for url in (self.url, reverse("blog:photo", args=[1])):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn("/cuenta/entrar/", response.url)

    def test_message_only_post(self):
        self.assertRedirects(self.post(body="Hola a todos"), self.url)
        post = Post.objects.get()
        self.assertEqual((post.author, post.body, post.has_image), (self.author, "Hola a todos", False))
        self.assertContains(self.client.get(self.url), "Hola a todos")

    def test_needs_a_message_or_a_photo(self):
        response = self.post(body="   ")
        self.assertContains(response, "Escribe un mensaje o añade una foto.")
        self.assertFalse(Post.objects.exists())

    def test_message_is_escaped(self):
        self.post(body="<b>negrita</b>")
        response = self.client.get(self.url)
        self.assertContains(response, "&lt;b&gt;negrita&lt;/b&gt;")
        self.assertNotContains(response, "<b>negrita</b>")

    def test_photo_is_stored_as_a_reduced_jpeg(self):
        self.assertRedirects(self.post(photo=png(size=(3200, 1000), mode="RGBA", color=(10, 200, 10, 128))), self.url)
        post = Post.objects.get()
        stored = Image.open(BytesIO(bytes(post.image)))
        self.assertEqual(stored.format, "JPEG")
        self.assertEqual(stored.size, (1600, 500))
        self.assertEqual((post.image_width, post.image_height), (1600, 500))

        response = self.client.get(reverse("blog:photo", args=[post.pk]))
        self.assertEqual(response["Content-Type"], "image/jpeg")
        self.assertIn("private", response["Cache-Control"])
        self.assertEqual(response.content, bytes(post.image))

    def test_photo_endpoint_is_404_without_photo(self):
        self.post(body="Sin foto")
        response = self.client.get(reverse("blog:photo", args=[Post.objects.get().pk]))
        self.assertEqual(response.status_code, 404)

    def test_rejects_a_file_that_is_not_a_photo(self):
        fake = SimpleUploadedFile("foto.png", b"<script>alert(1)</script>", "image/png")
        response = self.post(body="Mira", photo=fake)
        self.assertContains(response, "no es una foto")
        self.assertFalse(Post.objects.exists())

    def test_rejects_a_photo_over_the_size_limit(self):
        with mock.patch("blog.uploads.MAX_UPLOAD_BYTES", 2000):
            response = self.post(body="Mi dibujo", photo=noisy_png())
        self.assertContains(response, "La foto pesa más de")
        self.assertNotContains(response, "Escribe un mensaje o añade una foto.")
        self.assertContains(response, "Mi dibujo")
        self.assertFalse(Post.objects.exists())

    def test_feed_does_not_load_photo_bytes(self):
        self.post(photo=png())
        post = self.client.get(self.url).context["page"][0]
        self.assertIn("image", post.get_deferred_fields())
        self.assertTrue(post.has_image)

    def test_tagged_courses_link_from_the_photo_and_filter_the_feed(self):
        self.post(photo=png(), courses=[self.course.pk])
        self.post(body="Sin etiqueta")
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{self.course.get_absolute_url()}"')
        self.assertEqual(len(response.context["page"]), 2)

        filtered = self.client.get(self.url, {"curso": self.course.slug})
        self.assertEqual(len(filtered.context["page"]), 1)
        self.assertEqual(self.client.get(self.url, {"curso": "no-existe"}).status_code, 404)

        self.client.post(reverse("courses:enroll", args=[self.course.slug]))
        self.assertContains(self.client.get(self.course.get_absolute_url()), "1 publicación del blog")

    def test_cannot_tag_unpublished_courses_or_more_than_five(self):
        self.assertEqual(self.post(body="x", courses=[self.hidden.pk]).status_code, 200)
        many = [Course.objects.create(title=f"Curso {n}").pk for n in range(6)]
        self.assertContains(self.post(body="x", courses=many), "5 cursos como máximo")
        self.assertFalse(Post.objects.exists())

    def test_daily_limit(self):
        with mock.patch("blog.forms.DAILY_POST_LIMIT", 2):
            self.post(body="uno")
            self.post(body="dos")
            response = self.post(body="tres")
        self.assertContains(response, "límite de 2 publicaciones")
        self.assertEqual(Post.objects.count(), 2)

    def test_only_author_and_admin_can_delete(self):
        self.post(body="uno")
        self.post(body="dos")
        first, second = Post.objects.order_by("id")
        delete_first = reverse("blog:delete_post", args=[first.pk])

        self.assertEqual(self.client.get(delete_first).status_code, 405)
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(delete_first).status_code, 403)
        self.assertNotContains(self.client.get(self.url), delete_first)
        self.assertEqual(Post.objects.count(), 2)

        self.client.force_login(self.admin)
        self.assertRedirects(self.client.post(delete_first), self.url)
        self.client.force_login(self.author)
        self.client.post(reverse("blog:delete_post", args=[second.pk]))
        self.assertFalse(Post.objects.exists())
