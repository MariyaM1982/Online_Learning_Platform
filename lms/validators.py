import re
from rest_framework import serializers


class YouTubeLinkValidator:
    """
    Валидатор, разрешающий ссылки только на youtube.com
    """
    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        # Получаем значение поля, например video_url
        url = value.get(self.field)
        if url:
            # Проверяем, содержит ли ссылка youtube.com
            if not re.match(r'^https?://(www\.)?youtube\.com/', url) and \
               not re.match(r'^https?://(www\.)?youtu\.be/', url):
                raise serializers.ValidationError(
                    f'В поле {self.field} разрешены только ссылки на YouTube.'
                )