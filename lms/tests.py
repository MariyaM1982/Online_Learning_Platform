import self
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from .models import Course, Lesson, Subscription
from .validators import YouTubeLinkValidator
from rest_framework.test import APITestCase, APIRequestFactory

User = get_user_model()

class YouTubeLinkValidatorTest(TestCase):
    def setUp(self):
        self.validator = YouTubeLinkValidator(field='video_url')

    def test_valid_youtube_links(self):
        self.validator({'video_url': 'https://youtube.com/watch?v=123'})
        self.validator({'video_url': 'https://www.youtube.com/watch?v=123'})
        self.validator({'video_url': 'https://youtu.be/123'})
        # Ошибок быть не должно

    def test_invalid_links(self):
        with self.assertRaises(ValidationError):
            self.validator({'video_url': 'https://vk.com/video123'})

        with self.assertRaises(ValidationError):
            self.validator({'video_url': 'https://example.com'})

class LessonSubscriptionTestCase(APITestCase):
    def setUp(self):
        """Создаём тестовые данные и группу 'Модераторы'"""
        # Создаём группу "Модераторы"
        moderators_group, created = Group.objects.get_or_create(name='Модераторы')

                # Пользователи
        self.user = User.objects.create_user(email='user@test.com', password='pass')
        self.moderator = User.objects.create_user(email='moderator@test.com', password='pass')
        self.moderator.groups.add(moderators_group)

        # Курс
        self.course = Course.objects.create(
            title="Тестовый курс",
            description="Описание",
            owner=self.user
        )

        # Урок
        self.lesson = Lesson.objects.create(
            title="Тестовый урок",
            description="Описание урока",
            video_url="https://youtube.com/watch?v=123",
            course=self.course,
            owner=self.user
        )

        # Фабрика запросов
        self.factory = APIRequestFactory()

    def test_lesson_create(self):
        """Только владелец или модератор может создать урок"""
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Новый урок",
            "description": "Описание",
            "video_url": "https://youtube.com/watch?v=456",
            "course": self.course.id
        }
        response = self.client.post('/api/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_lesson_update_by_owner(self):
        """Владелец может редактировать урок"""
        self.client.force_authenticate(user=self.user)
        data = {"title": "Обновлённый урок"}
        response = self.client.patch(f'/api/lessons/{self.lesson.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_update_by_moderator(self):
        """Модератор может редактировать урок"""
        self.client.force_authenticate(user=self.moderator)
        data = {"title": "Отредактировано модератором"}
        response = self.client.patch(f'/api/lessons/{self.lesson.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_update_by_other_user(self):
        """Другой пользователь не может редактировать чужой урок"""
        other_user = User.objects.create_user(email='other@test.com', password='pass')
        self.client.force_authenticate(user=other_user)
        data = {"title": "Попытка взлома"}

        response = self.client.patch(f'/api/lessons/{self.lesson.id}/', data)

        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_lesson_delete_by_owner(self):
        """Владелец может удалить урок"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_lesson_delete_by_moderator(self):
        """Модератор не может удалить урок (по заданию)"""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_subscribe_to_course(self):
        """Пользователь может подписаться на курс"""
        self.client.force_authenticate(user=self.user)
        data = {"course_id": self.course.id}
        response = self.client.post('/api/subscribe/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')

    def test_unsubscribe_from_course(self):
        """Пользователь может отписаться от курса"""
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        data = {"course_id": self.course.id}
        response = self.client.post('/api/subscribe/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')

    def test_subscription_status_in_course(self):
        self.client.force_authenticate(user=self.user)
        Subscription.objects.create(user=self.user, course=self.course)

        url = reverse('course-detail', kwargs={'pk': self.course.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_subscribed'])

    def test_unauthorized_user_cannot_create_lesson(self):
        """Неавторизованный пользователь не может создать урок"""
        data = {
            "title": "Урок без доступа",
            "course": self.course.id,
            "video_url": "https://youtube.com/watch?v=123"
        }
        response = self.client.post('/api/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)