from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from users.tasks import block_inactive_users


class UserCeleryTests(APITestCase):

    def setUp(self) -> None:
        User = get_user_model()
        now = timezone.now()

        # Используем .create(), чтобы избежать проблем с обязательным полем username
        self.active_user = User.objects.create(
            email="active@test.com", last_login=now, is_active=True
        )
        self.active_user.set_password("password")
        self.active_user.save()

        self.inactive_user = User.objects.create(
            email="inactive@test.com",
            last_login=now - timedelta(days=35),
            is_active=True,
        )
        self.inactive_user.set_password("password")
        self.inactive_user.save()

        self.new_user_no_login = User.objects.create(
            email="new_no_login@test.com", last_login=None, is_active=True
        )
        self.new_user_no_login.date_joined = now
        self.new_user_no_login.set_password("password")
        self.new_user_no_login.save()

        self.old_user_no_login = User.objects.create(
            email="old_no_login@test.com", last_login=None, is_active=True
        )
        self.old_user_no_login.date_joined = now - timedelta(days=35)
        self.old_user_no_login.set_password("password")
        self.old_user_no_login.save()

    def test_block_inactive_users_task(self) -> None:
        """Проверка, что задача отключает пользователей, не заходивших > 30 дней"""
        blocked_count = block_inactive_users()

        self.assertEqual(blocked_count, 2)

        self.active_user.refresh_from_db()
        self.inactive_user.refresh_from_db()
        self.new_user_no_login.refresh_from_db()
        self.old_user_no_login.refresh_from_db()

        self.assertTrue(self.active_user.is_active)
        self.assertFalse(self.inactive_user.is_active)
        self.assertTrue(self.new_user_no_login.is_active)
        self.assertFalse(self.old_user_no_login.is_active)
