from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    object = CustomUserManager()

    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, default='+380 ')

    is_editor = models.BooleanField(blank=True, default=False)
    is_manager = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.email





