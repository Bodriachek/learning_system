from django.shortcuts import render
from rest_framework import viewsets, permissions

from users.models import CustomUser
from users.serializers import UserSerializer


class UsersViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = permissions.IsAdminUser
    http_method_names = ['get', 'retrieve', 'patch']
