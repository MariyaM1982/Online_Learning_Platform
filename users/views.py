from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserProfileSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Получение и редактирование профиля текущего пользователя
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Возвращаем текущего пользователя
        return self.request.user