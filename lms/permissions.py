from rest_framework import permissions
from users.permissions import IsModerator


class IsOwnerOrModerator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Админ — всегда может
        if request.user.is_superuser:
            return True

        # Модератор — может только если метод не DELETE
        if request.user.groups.filter(name='Модераторы').exists():
            if request.method != 'DELETE':
                return True

        # Владелец — может всё
        return obj.owner == request.user