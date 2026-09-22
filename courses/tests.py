from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import Course


class CourseCeleryTests(APITestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create(
            email="owner@example.com",
        )
        self.user.set_password("password")
        self.user.save()

        self.course = Course.objects.create(
            title="Python",
            owner=self.user,
        )
        self.client.force_authenticate(self.user)

    # Патчим сразу оба места для 100% перехвата вызова Celery
    @patch("courses.tasks.send_course_update_email.delay")
    @patch("courses.views.send_course_update_email.delay")
    def test_update_course_starts_celery_task(self, views_mock, tasks_mock) -> None:
        """Проверяет постановку таски в очередь при PATCH запросе"""
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.patch(
                reverse("courses:courses-detail", args=[self.course.pk]),
                {"title": "Advanced Python"},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что хотя бы один из моков зафиксировал вызов
        self.assertTrue(views_mock.called or tasks_mock.called)
