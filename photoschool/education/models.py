import reversion
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.functional import cached_property

from users.models import CustomUser
from django.utils.translation import gettext_lazy as _


@reversion.register()
class Program(models.Model):
    is_approved = models.BooleanField(default=False)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=255)

    def __str__(self):
        return self.title

    @cached_property
    def first_lesson(self):
        return self.lessons.first()


@reversion.register()
class Theme(models.Model):
    is_approved = models.BooleanField(default=False)
    program = models.ForeignKey(Program, null=True, related_name='themes', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=255)

    def __str__(self):
        return self.title


@reversion.register()
class Lesson(models.Model):
    is_approved = models.BooleanField(default=False)
    title = models.CharField(max_length=100)
    program = models.ForeignKey(Program, null=True, related_name='lessons', on_delete=models.CASCADE)
    theme = models.ForeignKey(Theme, blank=True, null=True, related_name='lessons', on_delete=models.CASCADE)
    description = models.TextField(max_length=255)
    theory = models.TextField(max_length=2000)
    practice = models.CharField(max_length=150)
    answer = models.CharField(max_length=150)

    def __str__(self):
        return self.title


class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='students')
    wish_program = models.ManyToManyField(Program, null=True, blank=True)
    open_program = models.ManyToManyField(Program, related_name='students', null=True, blank=True)


class Studying(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='studying')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='studying')
    answer = models.CharField(max_length=150)
    passed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        right_answer = self.lesson.answer
        self.passed = bool(self.answer == right_answer)
        super(Studying, self).save(*args, **kwargs)




