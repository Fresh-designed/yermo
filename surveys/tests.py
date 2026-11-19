from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import SurveyResponse
from .stats import survey_summary

User = get_user_model()

VALID = {
    "full_name": "Nadia Pérez",
    "age": "21",
    "career": "Diseño gráfico",
    "overall": "5",
    "content": "4",
    "ease": "3",
    "recommend": "si",
    "comment": "Más cursos de Blender.",
}


class SurveyTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("nadia", "nadia@example.com", "x")
        self.url = reverse("surveys:survey")
        self.client.force_login(self.user)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/cuenta/entrar/", response.url)

    def test_saves_one_response_per_user_and_lets_them_change_it(self):
        self.assertRedirects(self.client.post(self.url, VALID), self.url)
        answer = SurveyResponse.objects.get()
        self.assertEqual((answer.user, answer.overall, answer.content, answer.ease), (self.user, 5, 4, 3))
        self.assertEqual((answer.full_name, answer.age, answer.career), ("Nadia Pérez", 21, "Diseño gráfico"))
        self.assertTrue(answer.recommend)

        self.client.post(self.url, {**VALID, "overall": "2", "recommend": "no"})
        answer = SurveyResponse.objects.get()
        self.assertEqual(answer.overall, 2)
        self.assertFalse(answer.recommend)

    def test_rejects_values_outside_the_scale(self):
        for bad in ("0", "6", "abc", ""):
            response = self.client.post(self.url, {**VALID, "overall": bad})
            self.assertEqual(response.status_code, 200, bad)
        self.assertFalse(SurveyResponse.objects.exists())

    def test_every_question_but_the_comment_is_required(self):
        for name in ("full_name", "age", "career", "overall", "content", "ease", "recommend"):
            data = {key: value for key, value in VALID.items() if key != name}
            self.assertEqual(self.client.post(self.url, data).status_code, 200, name)
        self.assertFalse(SurveyResponse.objects.exists())
        self.client.post(self.url, {**VALID, "comment": ""})
        self.assertTrue(SurveyResponse.objects.exists())

    def test_age_must_be_a_whole_number_in_range(self):
        for bad in ("9", "101", "veinte", "20.5", "-3"):
            response = self.client.post(self.url, {**VALID, "age": bad})
            self.assertEqual(response.status_code, 200, bad)
        self.assertFalse(SurveyResponse.objects.exists())

    def test_name_and_career_spaces_are_tidied(self):
        self.client.post(self.url, {**VALID, "full_name": "  Nadia   Pérez ", "career": " Diseño   gráfico"})
        answer = SurveyResponse.objects.get()
        self.assertEqual((answer.full_name, answer.career), ("Nadia Pérez", "Diseño gráfico"))
        self.assertFalse(self.client.post(self.url, {**VALID, "full_name": "   "}).context["form"].is_valid())

    def test_form_shows_previous_answers(self):
        self.client.post(self.url, {**VALID, "recommend": "no"})
        form = self.client.get(self.url).context["form"]
        self.assertEqual(form["overall"].value(), 5)
        self.assertEqual((form["full_name"].value(), form["age"].value()), ("Nadia Pérez", 21))
        self.assertEqual(form["recommend"].value(), "no")

    def test_my_courses_invites_until_answered(self):
        my_courses = reverse("courses:my_courses")
        self.assertContains(self.client.get(my_courses), "Responder la encuesta")
        self.client.post(self.url, VALID)
        self.assertNotContains(self.client.get(my_courses), "Responder la encuesta")


class SummaryTests(TestCase):
    def test_empty(self):
        summary = survey_summary()
        self.assertEqual(summary["total"], 0)
        self.assertEqual(summary["recommend_percent"], 0)
        self.assertEqual([row["count"] for row in summary["distribution"]], [0, 0, 0, 0, 0])

    def test_averages_distribution_and_comments(self):
        answers = [(5, True, "Me encanta."), (5, True, ""), (2, False, "Faltan cursos.")]
        for index, (overall, recommend, comment) in enumerate(answers):
            user = User.objects.create_user(f"u{index}", f"u{index}@example.com", "x")
            SurveyResponse.objects.create(
                user=user, overall=overall, content=4, ease=3, recommend=recommend, comment=comment
            )
        summary = survey_summary()
        self.assertEqual(summary["total"], 3)
        self.assertEqual([item["value"] for item in summary["averages"]], [4.0, 4.0, 3.0])
        self.assertEqual(summary["recommend_percent"], 67)
        by_score = {row["score"]: row for row in summary["distribution"]}
        self.assertEqual((by_score[5]["count"], by_score[5]["width"]), (2, 100))
        self.assertEqual((by_score[2]["count"], by_score[2]["width"]), (1, 50))
        self.assertEqual(by_score[3]["count"], 0)
        self.assertEqual({answer.comment for answer in summary["comments"]}, {"Me encanta.", "Faltan cursos."})

    def test_age_and_careers(self):
        people = [("Ana", 20, "Diseño gráfico"), ("Luis", 24, "diseño gráfico"), ("Eva", 31, "Animación"), ("Sin datos", None, "")]
        for index, (name, age, career) in enumerate(people):
            user = User.objects.create_user(f"p{index}", f"p{index}@example.com", "x")
            SurveyResponse.objects.create(
                user=user, full_name=name, age=age, career=career, overall=4, content=4, ease=4, recommend=True
            )
        summary = survey_summary()
        self.assertEqual(summary["age"], 25)
        self.assertEqual(
            [(row["label"], row["count"], row["width"]) for row in summary["careers"]],
            [("Diseño gráfico", 2, 100), ("Animación", 1, 50)],
        )

    def test_dashboard_shows_people_data(self):
        admin = User.objects.create_user("ada", "ada@example.com", "x", is_staff=True, is_superuser=True)
        user = User.objects.create_user("omar", "omar@example.com", "x")
        SurveyResponse.objects.create(
            user=user, full_name="Omar Ruiz", age=22, career="Animación", overall=5, content=5, ease=5,
            recommend=True, comment="Genial.",
        )
        self.client.force_login(admin)
        response = self.client.get(reverse("metrics:dashboard"))
        self.assertContains(response, "<strong>Omar Ruiz</strong> (Animación, 22 años) · 5 de 5: Genial.", html=False)
        self.assertContains(response, "Edad promedio")
        self.assertContains(response, "Respuestas por carrera")
        self.assertContains(response, reverse("admin:surveys_surveyresponse_changelist"))
