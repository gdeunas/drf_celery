from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone

User = get_user_model()


@shared_task
def block_inactive_users() -> int:
    user_model = get_user_model()
    cutoff = timezone.now() - timedelta(days=30)

    return (
        user_model.objects.filter(is_active=True)
        .filter(
            Q(last_login__lt=cutoff)
            | Q(last_login__isnull=True, date_joined__lt=cutoff)
        )
        .update(is_active=False)
    )
