from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .validators import YouTubeLinkValidator


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        validators = [YouTubeLinkValidator(field='video_url')]


class CourseSerializer(serializers.ModelSerializer):
    lesson_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_lesson_count(self, obj):
        return obj.lessons.count() if hasattr(obj, 'lessons') else obj.lesson_set.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False