from django.contrib import admin

from .models import *


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    list_display_links = ('id', 'title')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    list_display_links = ('id', 'title')


@admin.register(Studying)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'lesson', 'passed')
    list_display_links = ('id', 'lesson')


admin.site.register(Theme)
admin.site.register(Student)
