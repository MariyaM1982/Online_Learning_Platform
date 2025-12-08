from rest_framework import permissions

class IsModerator(permissions.BasePermission):
    """
    Проверяет, состоит ли пользователь в группе 'Модераторы'
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Модераторы').exists()