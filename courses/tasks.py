from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_course_update_email(course_id):
    from courses.models import Course, Subscription

    try:
        course = Course.objects.get(pk=course_id)
        subscriptions = Subscription.objects.filter(course=course, is_active=True)

        recipient_list = [sub.user.email for sub in subscriptions if sub.user.email]

        if recipient_list:
            send_mail(
                subject=f"Обновление материалов курса: {course.title}",
                message=f"Здравствуйте! Материалы курса '{course.title}', на который вы подписаны, были обновлены.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=recipient_list,
                fail_silently=False,
            )
    except Course.DoesNotExist:
        pass
