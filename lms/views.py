from rest_framework import viewsets, generics, permissions
from users.permissions import IsModerator
from .models import Course, Lesson
from .permissions import IsOwnerOrModerator
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    CRUD для курсов через ViewSet
    Доступны: GET, POST, PUT, PATCH, DELETE
    """
    queryset = Course.objects.prefetch_related('lessons').all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

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
    serializer_class = LessonSerializer
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
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if self.request.user.groups.filter(name='Модераторы').exists() or self.request.user.is_superuser:
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)