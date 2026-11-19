from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone

from blog.models import Post
from surveys.models import SurveyResponse

from .charts import _axis_ticks
from .models import ActivityEvent

User = get_user_model()
Kind = ActivityEvent.Kind


class AxisTests(SimpleTestCase):
    def test_ticks_are_round_and_cover_the_peak(self):
        self.assertEqual(_axis_ticks(0), [0, 1, 2, 3, 4])
        self.assertEqual(_axis_ticks(7), [0, 2, 4, 6, 8])
        self.assertEqual(_axis_ticks(18), [0, 5, 10, 15, 20])
        self.assertEqual(_axis_ticks(130), [0, 50, 100, 150])


class AccessTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("ada", "ada@example.com", "x", is_staff=True)
        self.user = User.objects.create_user("omar", "omar@example.com", "x")
        self.url = reverse("metrics:dashboard")

    def test_anonymous_goes_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/cuenta/entrar/", response.url)

    def test_ordinary_user_gets_403(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.url).status_code, 403)
        delete_url = reverse("metrics:delete_user", args=[self.admin.pk])
        self.assertEqual(self.client.post(delete_url).status_code, 403)
        self.assertTrue(User.objects.filter(pk=self.admin.pk).exists())

    def test_admin_sees_dashboard(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_users"], 2)
        self.assertEqual(response.context["admin_users"], 1)
        self.assertEqual(response.context["ordinary_users"], 1)

    def test_nav_link_only_for_admins(self):
        self.client.force_login(self.user)
        self.assertNotContains(self.client.get(reverse("courses:catalog")), self.url)
        self.client.force_login(self.admin)
        self.assertContains(self.client.get(reverse("courses:catalog")), self.url)

    def test_dashboard_has_a_delete_button_for_every_other_account(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertContains(response, reverse("metrics:delete_user", args=[self.user.pk]))
        self.assertNotContains(response, reverse("metrics:delete_user", args=[self.admin.pk]))

    def test_dashboard_shows_survey_results(self):
        self.client.force_login(self.admin)
        self.assertContains(self.client.get(self.url), "Nadie ha respondido la encuesta todavía")
        SurveyResponse.objects.create(
            user=self.user, overall=4, content=5, ease=3, recommend=True, comment="Todo bien."
        )
        response = self.client.get(self.url)
        self.assertEqual(response.context["survey"]["total"], 1)
        self.assertContains(response, "Todo bien.")
        self.assertContains(response, "100%")


class FlowTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("ada", "ada@example.com", "x", is_staff=True)
        self.client.force_login(self.admin)

    def test_registration_login_and_visit_are_recorded(self):
        kinds = set(ActivityEvent.objects.values_list("kind", flat=True))
        self.assertIn(Kind.REGISTER, kinds)
        self.assertIn(Kind.LOGIN, kinds)
        self.client.get(reverse("courses:catalog"))
        self.client.get(reverse("courses:catalog"))
        self.assertEqual(ActivityEvent.objects.filter(kind=Kind.VISIT).count(), 1)

    def test_flow_has_one_row_per_day_including_empty_days(self):
        ActivityEvent.objects.create(
            kind=Kind.LOGIN, username="x", created_at=timezone.now() - timedelta(days=3)
        )
        ActivityEvent.objects.create(
            kind=Kind.LOGIN, username="viejo", created_at=timezone.now() - timedelta(days=40)
        )
        flow = self.client.get(reverse("metrics:dashboard"), {"dias": 7}).context["flow"]
        self.assertEqual(len(flow), 7)
        self.assertEqual(flow[-4]["logins"], 1)
        self.assertEqual(flow[-1]["day"], timezone.localdate())

    def test_invalid_range_uses_default(self):
        response = self.client.get(reverse("metrics:dashboard"), {"dias": "abc"})
        self.assertEqual(response.context["days"], 14)


class DeleteUserTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("ada", "ada@example.com", "x", is_staff=True)
        self.target = User.objects.create_user("omar", "omar@example.com", "x")
        self.client.force_login(self.admin)

    def url(self, user):
        return reverse("metrics:delete_user", args=[user.pk])

    def test_get_only_asks_for_confirmation(self):
        self.assertContains(self.client.get(self.url(self.target)), "omar")
        self.assertTrue(User.objects.filter(pk=self.target.pk).exists())

    def test_post_deletes_and_keeps_the_event(self):
        self.client.post(self.url(self.target))
        self.assertFalse(User.objects.filter(pk=self.target.pk).exists())
        event = ActivityEvent.objects.get(kind=Kind.DELETE)
        self.assertEqual(event.username, "omar")
        self.assertTrue(ActivityEvent.objects.filter(kind=Kind.REGISTER, username="omar").exists())
        self.assertEqual(self.client.get(reverse("metrics:dashboard")).context["all_deletes"], 1)

    def test_deleting_an_account_removes_its_posts_and_survey_answer(self):
        Post.objects.create(author=self.target, body="Hola")
        SurveyResponse.objects.create(user=self.target, overall=3, content=3, ease=3, recommend=False)
        self.client.post(self.url(self.target))
        self.assertFalse(Post.objects.exists())
        self.assertFalse(SurveyResponse.objects.exists())

    def test_cannot_delete_yourself(self):
        self.client.post(self.url(self.admin))
        self.assertTrue(User.objects.filter(pk=self.admin.pk).exists())

    def test_admin_can_delete_another_admin(self):
        other = User.objects.create_user("ines", "ines@example.com", "x", is_staff=True)
        self.client.post(self.url(other))
        self.assertFalse(User.objects.filter(pk=other.pk).exists())
