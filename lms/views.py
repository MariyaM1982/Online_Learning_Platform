from rest_framework import viewsets, generics
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    CRUD для курсов через ViewSet
    Доступны: GET, POST, PUT, PATCH, DELETE
    """
    queryset = Course.objects.prefetch_related('lessons').all()
    serializer_class = CourseSerializer

class LessonListCreateAPIView(generics.ListCreateAPIView):
    """Получение списка уроков и создание нового"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Просмотр, изменение и удаление урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer