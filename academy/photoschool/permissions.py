from rest_framework import permissions


class IsStudyingOwnerPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return bool(user and hasattr(user, 'student'))

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view) and obj.student.user == request.user


class IsStaffPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and bool(
                user.is_editor or user.is_manager or user.is_superuser
            )
        )


class IsManagerOrSuperUserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and bool(
                user.is_manager or user.is_superuser
            )
        )


class IsSuperUserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_superuser)
