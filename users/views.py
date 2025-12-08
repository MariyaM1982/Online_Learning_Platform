from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .filters import PaymentFilter
from .models import User, Payment
from .serializers import UserProfileSerializer, PaymentSerializer, UserRegisterSerializer


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]  # Открыт для всех

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Получение и редактирование профиля текущего пользователя
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Возвращаем текущего пользователя
        return self.request.user

class PaymentListAPIView(generics.ListAPIView):
    """
    Вывод списка платежей с фильтрацией:
    - ?ordering=payment_date — по возрастанию даты
    - ?ordering=-payment_date — по убыванию
    - ?paid_course=1 — только по курсу с id=1
    - ?paid_lesson=2 — только по уроку с id=2
    - ?payment_method=transfer — только переводы
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PaymentFilter