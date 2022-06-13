from django.contrib import admin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'is_editor', 'is_manager')
    list_display_links = ('id', 'first_name')


