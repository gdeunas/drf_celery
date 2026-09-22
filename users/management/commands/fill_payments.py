# users/management/commands/fill_payments.py
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from users.models import Payment

User = get_user_model()


class Command(BaseCommand):
    help = "Заполнение базы данных тестовыми платежами"

    def handle(self, *args, **options):
        user = User.objects.first()

        if not user:
            self.stdout.write(
                self.style.ERROR("Сначала создайте хотя бы одного пользователя!")
            )
            return

        Payment.objects.all().delete()

        Payment.objects.create(
            user=user,
            amount=5000.00,
            payment_method=Payment.TRANSFER,
        )

        Payment.objects.create(
            user=user,
            amount=1500.00,
            payment_method=Payment.CASH,
        )

        self.stdout.write(self.style.SUCCESS("Данные по платежам успешно добавлены!"))
