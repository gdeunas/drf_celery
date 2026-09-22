from datetime import timedelta
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from users.tasks import check_inactive_users


class UserCeleryTests(APITestCase):

    def setUp(self) -> None:
        User = get_user_model()

        # Активный пользователь (заходил недавно)
        self.active_user = User.objects.create_user(
            email="active@test.com", password="password", last_login=timezone.now()
        )

        # Неактивный пользователь (заходил больше месяца назад)
        self.inactive_user = User.objects.create_user(
            email="inactive@test.com",
            password="password",
            last_login=timezone.now() - timedelta(days=35),
        )

    def test_block_inactive_users_task(self) -> None:
        """Проверка, что задача отключает пользователей, не заходивших > 30 дней"""
        # Убедимся, что изначально оба пользователя активны
        self.assertTrue(self.active_user.is_active)
        self.assertTrue(self.inactive_user.is_active)

        # Запускаем периодическую задачу синхронно
        check_inactive_users()

        # Обновляем данные из базы данных
        self.active_user.refresh_from_db()
        self.inactive_user.refresh_from_db()

        # Проверяем результат: активный остался активным, старый заблокирован
        self.assertTrue(self.active_user.is_active)
        self.assertFalse(self.inactive_user.is_active)
