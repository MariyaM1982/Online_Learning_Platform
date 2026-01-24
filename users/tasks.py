from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta


User = get_user_model()


@shared_task
def deactivate_inactive_users():
    """
    Блокирует пользователей, которые не заходили более 30 дней
    """
    # Определяем дату: 30 дней назад
    cutoff_date = timezone.now() - timedelta(days=30)

    # Находим неактивных пользователей
    inactive_users = User.objects.filter(
        is_active=True,
        last_login__lt=cutoff_date
    )

    count = inactive_users.count()
    if count > 0:
        # Блокируем
        inactive_users.update(is_active=False)
        print(f"Заблокировано {count} неактивных пользователей.")
    else:
        print("Нет неактивных пользователей для блокировки.")

    return f"Обработано пользователей: {count}"