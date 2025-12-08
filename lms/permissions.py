from rest_framework import permissions
from users.permissions import IsModerator


class IsOwnerOrModerator(permissions.BasePermission):
    """
    Разрешает доступ:
    - Владельцу объекта
    - Модераторам
    - Администраторам
    """
    def has_object_permission(self, request, view, obj):
        # Все модераторы и админы — могут
        if IsModerator().has_permission(request, view):
            return True
        # Владелец — может
        return obj.owner == request.user