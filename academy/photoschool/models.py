import reversion

from django.db import models
from django.utils.functional import cached_property
from reversion.models import Version

from users.models import CustomUser


@reversion.register()
class Program(models.Model):
    is_approved = models.BooleanField(default=False)
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=255)

    def __str__(self):
        return self.title

    @cached_property
    def first_lesson(self):
        return self.lessons.first()

    @property
    def actual_version(self):
        for version in Version.objects.get_for_object(self):
            field_dict = version.field_dict
            field_dict['editor'] = version.revision.user.username
            if field_dict['is_approved']:
                return field_dict


@reversion.register()
class Theme(models.Model):
    is_approved = models.BooleanField(default=False)
    program = models.ForeignKey(Program, related_name='themes', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=255)

    def __str__(self):
        return self.title

    @property
    def actual_version(self):
        for version in Version.objects.get_for_object(self):
            field_dict = version.field_dict
            field_dict['editor'] = version.revision.user.username
            if field_dict['is_approved']:
                return field_dict


@reversion.register()
class Lesson(models.Model):
    class Meta:
        ordering = ('id',)

    parent = models.OneToOneField('self', related_name='child', on_delete=models.CASCADE, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    editor = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='lesson')
    title = models.CharField(max_length=100)
    program = models.ForeignKey(Program, related_name='lessons', on_delete=models.CASCADE)
    theme = models.ForeignKey(Theme, blank=True, null=True, related_name='lessons', on_delete=models.CASCADE)
    theory = models.TextField(max_length=2000)
    practice = models.CharField(max_length=150)
    answer = models.CharField(max_length=150)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.answer = str(self.answer).lower()

            program_lessons = self.program.lessons.all()
            if program_lessons:
                self.parent = list(program_lessons)[-1]
        super().save(*args, **kwargs)

    @property
    def actual_version(self):
        for version in Version.objects.get_for_object(self):
            field_dict = version.field_dict
            field_dict['editor'] = version.revision.user.username
            if field_dict['is_approved']:
                return field_dict


class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student')
    wish_programs = models.ManyToManyField(Program, blank=True)
    open_programs = models.ManyToManyField(Program, related_name='students', blank=True)


class Studying(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='studying')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='studying')
    answer = models.CharField(max_length=150)
    passed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        right_answer = self.lesson.answer
        self.passed = bool(str(self.answer).lower() == right_answer)
        if self.passed and hasattr(self.lesson, 'child'):
            Studying.objects.get_or_create(lesson=self.lesson.child, student=self.student)
        super(Studying, self).save(*args, **kwargs)




