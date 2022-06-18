from rest_framework import permissions


class IsStudentOrSuperUser(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return bool(user and hasattr(user, 'student') or user.is_superuser)


# class IsEditorOrSuperUser(permissions.BasePermission):
#
#     def has_permission(self, request, view):
#         user = request.user
#         return bool(user and  user.is_editor)


