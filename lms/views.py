from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import viewsets, generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.permissions import IsModerator
from .models import Course, Lesson, Subscription
from .permissions import IsOwnerOrModerator
from .serializers import CourseSerializer, LessonSerializer
from .paginators import CourseLessonPagination


class CourseViewSet(viewsets.ModelViewSet):
    """
    CRUD для курсов через ViewSet
    Доступны: GET, POST, PUT, PATCH, DELETE
    """
    queryset = Course.objects.prefetch_related('lessons').all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CourseLessonPagination

    def get_queryset(self):
        # Модераторы и админы видят всё
        if self.request.user.groups.filter(name='Модераторы').exists() or self.request.user.is_superuser:
            return Course.objects.all()
        # Обычные пользователи — только свои
        return Course.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]



class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = CourseLessonPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.groups.filter(name='Модераторы').exists() or self.request.user.is_superuser:
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        lesson = serializer.save(owner=self.request.user)
        # Привязываем урок к курсу
        course = lesson.course
        if course.owner != self.request.user and not self.request.user.groups.filter(name='Модераторы').exists():
            raise permissions.PermissionDenied("Вы можете добавлять уроки только в свои курсы.")

    def get_permissions(self):
        if self.request.method == 'POST':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]
        elif self.request.method == 'DELETE':
            # ✅ Владелец и админ — могут удалять, модераторы — нет
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Модераторы').exists() or user.is_superuser:
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

@extend_schema(
    description="Управление подпиской пользователя на курс. "
                "Если подписка есть — удаляется, если нет — создаётся.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'course_id': {
                    'type': 'integer',
                    'example': 1,
                    'description': 'ID курса, на который подписываемся'
                }
            },
            'required': ['course_id']
        }
    },
    responses={
        200: {
            'type': 'object',
            'properties': {
                'message': {
                    'type': 'string',
                    'example': 'Подписка добавлена'
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            'Subscribe',
            summary='Подписаться на курс',
            value={'course_id': 1},
            request_only=True
        ),
        OpenApiExample(
            'Unsubscribe',
            summary='Отписаться от курса',
            value={'message': 'Подписка удалена'},
            response_only=True
        )
    ]
)

class SubscriptionAPIView(APIView):
    """
    Управление подпиской пользователя на курс
    POST: подписаться/отписаться
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')
        course = get_object_or_404(Course, id=course_id)

        # Проверяем, есть ли уже подписка
        subs_item = Subscription.objects.filter(user=user, course=course)

        if subs_item.exists():
            subs_item.delete()
            message = 'Подписка удалена'
        else:
            Subscription.objects.create(user=user, course=course)
            message = 'Подписка добавлена'

        return Response({"message": message})