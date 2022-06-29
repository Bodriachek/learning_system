from django.apps import AppConfig


class PhotoschoolConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'photoschool'

    def ready(self):
        from .signals import create_studying  # noqa
