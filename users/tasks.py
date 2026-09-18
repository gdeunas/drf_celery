from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from celery import shared_task

User = get_user_model()


@shared_task
def block_inactive_users():
    """
    Фоновая задача для блокировки пользователей,
    которые не заходили в систему более месяца.
    """
    # Вычисляем дату месяц назад с учетом текущей таймзоны
    one_month_ago = timezone.now() - timedelta(days=30)

    # Фильтруем активных пользователей, у которых last_login меньше этой даты
    inactive_users = User.objects.filter(
        is_active=True,
        last_login__lt=one_month_ago
    )

    # Массово обновляем флаг ис_active для оптимизации запросов
    updated_count = inactive_users.update(is_active=False)

    return f"Успешно заблокировано пользователей: {updated_count}"
