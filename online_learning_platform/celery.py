from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from decouple import config

# Установите переменную окружения для Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_learning_platform.settings')

# Создаём экземпляр Celery
app = Celery('online_learning_platform')

# Загружаем настройки из Django с префиксом CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим задачи в приложениях Django
app.autodiscover_tasks()

# Опционально: тестовая задача
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')