from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Course
from .tasks import send_course_update_notification


@receiver(post_save, sender=Course)
def course_updated_handler(sender, instance, created, **kwargs):
    """
    При обновлении курса (не создании) — отправляем рассылку
    """
    if not created:  # Только при обновлении
        send_course_update_notification.delay(instance.id, instance.title)