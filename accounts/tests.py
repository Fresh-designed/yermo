from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

User = get_user_model()

VALID = {
    "username": "nadia",
    "email": "nadia@example.com",
    "password1": "duna-larga-7421",
    "password2": "duna-larga-7421",
}


class RegisterTests(TestCase):
    def post(self, **extra):
        return self.client.post(reverse("accounts:register"), {**VALID, **extra})

    def test_public_register_creates_ordinary_user(self):
        self.assertRedirects(self.post(), reverse("courses:catalog"), fetch_redirect_response=False)
        user = User.objects.get(username="nadia")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    @override_settings(ADMIN_REGISTRATION_CODE="clave-yermo")
    def test_correct_code_creates_admin(self):
        self.post(admin_code="clave-yermo")
        user = User.objects.get(username="nadia")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    @override_settings(ADMIN_REGISTRATION_CODE="clave-yermo")
    def test_wrong_code_is_rejected(self):
        response = self.post(admin_code="otra")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.exists())

    @override_settings(ADMIN_REGISTRATION_CODE="")
    def test_code_disabled_when_setting_is_empty(self):
        self.post(admin_code="cualquiera")
        self.assertFalse(User.objects.exists())

    def test_cannot_become_admin_by_posting_flags(self):
        self.post(is_staff="on", is_superuser="on")
        self.assertFalse(User.objects.get(username="nadia").is_staff)

    def test_duplicate_email_is_rejected_ignoring_case(self):
        User.objects.create_user("otra", "NADIA@example.com", "duna-larga-7421")
        response = self.post()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="nadia").exists())


class LoginTests(TestCase):
    def setUp(self):
        User.objects.create_user("nadia", "nadia@example.com", "duna-larga-7421")

    def login(self, username, password="duna-larga-7421"):
        return self.client.post(
            reverse("accounts:login"), {"username": username, "password": password}
        )

    def test_login_with_username_or_email(self):
        for identifier in ("nadia", "NADIA", "nadia@example.com"):
            self.assertEqual(self.login(identifier).status_code, 302, identifier)
            self.client.logout()

    def test_wrong_password_fails(self):
        self.assertEqual(self.login("nadia", "mala").status_code, 200)

    def test_protected_page_shows_login_notice(self):
        response = self.client.get(reverse("home"), follow=True)
        self.assertContains(response, "Inicia sesión para continuar.")
