from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import Course, Lesson, Subscription


@shared_task
def check_course_updates():
    print(f"Проверка обновлений курсов: {timezone.now()}")
    print(f"Всего курсов: {Course.objects.count()}")
    print(f"Всего уроков: {Lesson.objects.count()}")
    return "OK"

@shared_task
def send_course_update_notification(course_id, course_title):
    """
    Асинхронная рассылка уведомлений о обновлении курса
    """
    try:
        # Получаем всех подписчиков курса
        subscribers = Subscription.objects.filter(course_id=course_id).select_related('user')
        emails = [sub.user.email for sub in subscribers if sub.user.email]

        if not emails:
            return f"Нет подписчиков для курса {course_title}"

        # Отправляем письмо
        subject = f"Обновление курса: {course_title}"
        message = (
            f"Здравствуйте!\n\n"
            f"Курс '{course_title}' был обновлён. Заходите и посмотрите новые материалы!\n\n"
            f"С уважением,\n"
            f"Команда Online Learning Platform"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL or "noreply@online-learning.com",
            recipient_list=emails,
            fail_silently=False,
        )

        return f"Письма отправлены {len(emails)} подписчикам курса '{course_title}'"

    except Exception as e:
        # Логируем ошибку
        return f"Ошибка при отправке: {str(e)}"