from django.contrib import admin

from .models import *


class LessonInlineModel(admin.TabularInline):
    model = Lesson
    fields = [
        'is_approved',
        'editor',
        'parent',
        'title',
        'theme',
        'theory',
        'practice',
        'answer'
        ]


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    list_display_links = ('id', 'title')
    inlines = [
        LessonInlineModel,
    ]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'theme', 'program')
    list_display_links = ('id', 'title')


@admin.register(Studying)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'lesson', 'passed')
    list_display_links = ('id', 'lesson')


@admin.register(Student)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    list_display_links = ('id', 'user')


admin.site.register(Theme)
