from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import Course, Subscription
from courses.tasks import send_course_update_email


class CourseCeleryTests(APITestCase):

    def setUp(self) -> None:
        User = get_user_model()
        self.owner = User.objects.create_user(
            email="owner@test.com", password="password"
        )
        self.subscriber = User.objects.create_user(
            email="sub@test.com", password="password"
        )

        self.course = Course.objects.create(
            title="Python Basic",
            owner=self.owner,
        )
        # Создаем подписку для пользователя
        Subscription.objects.create(user=self.subscriber, course=self.course)

        self.client.force_authenticate(self.owner)

    @patch("courses.views.send_course_update_email.delay")
    def test_update_course_starts_celery_task(self, delay_mock) -> None:
        """Проверка, что обновление курса ставит задачу Celery в очередь"""
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.patch(
                reverse("courses:courses-detail", args=[self.course.pk]),
                {"title": "Python Advanced"},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что метод .delay() был вызван с ID курса
        delay_mock.assert_called_once_with(self.course.pk)

    @patch("courses.tasks.send_mail")  # Мокаем отправку почты внутри самой таски
    def test_send_course_update_email_task_selects_subscribers(
        self, send_mail_mock
    ) -> None:
        """Проверка работы самой Celery-задачи: выборка подписчиков"""
        # Вызываем таску напрямую (синхронно, без .delay)
        send_course_update_email(self.course.pk)

        # Проверяем, что send_mail был вызван для email подписчика
        send_mail_mock.assert_called_once()
        args, kwargs = send_mail_mock.call_args

        # Проверяем, что в списке получателей (recipient_list) есть наш подписчик
        self.assertIn(self.subscriber.email, kwargs.get("recipient_list", []))
