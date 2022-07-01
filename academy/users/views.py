from rest_framework import viewsets

from photoschool.permissions import IsSuperUserPermission
from users.models import CustomUser
from users.serializers import UserSerializer


class UsersViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSuperUserPermission]
    http_method_names = ['get', 'retrieve', 'patch']
