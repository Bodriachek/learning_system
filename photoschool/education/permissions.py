from rest_framework import permissions


class IsStudentPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return bool(user and hasattr(user, 'student'))

    def has_object_permission(self, request, view, obj):
        self.has_permission(request, view)
        return obj.user == request.user


class IsStudyingOwnerPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return bool(user and hasattr(user, 'student'))

    def has_object_permission(self, request, view, obj):
        self.has_permission(request, view)
        return obj.student.user == request.user


# class IsEditorOrSuperUser(permissions.BasePermission):
#
#     def has_permission(self, request, view):
#         user = request.user
#         return bool(user and  user.is_editor)


