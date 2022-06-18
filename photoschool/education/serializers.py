from rest_framework import serializers

from education.models import *


# ----------------------------------------------------------------------------------------------------------------------
# ____________________________________________________Program Block____________________________________________________
# ----------------------------------------------------------------------------------------------------------------------
class ProgramSerializer(serializers.ModelSerializer):

    class Meta:
        model = Program
        fields = '__all__'


class ProgramShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Program
        read_only_fields = ('title',)
        fields = ('title',)


class ProgramCRUDSerializer(serializers.ModelSerializer):

    class Meta:
        model = Program
        fields = ('id', 'title', 'description')


# ----------------------------------------------------------------------------------------------------------------------
# _____________________________________________________Theme Block_____________________________________________________
# ----------------------------------------------------------------------------------------------------------------------
class ThemeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Theme
        fields = '__all__'


class ThemeCRUDSerializer(serializers.ModelSerializer):

    class Meta:
        model = Theme
        fields = ('id', 'program', 'title', 'description')


# ----------------------------------------------------------------------------------------------------------------------
# _____________________________________________________Lesson Block_____________________________________________________
# ----------------------------------------------------------------------------------------------------------------------
class LessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = '__all__'


class LessonShortSerializer(serializers.ModelSerializer):
    program = ProgramShortSerializer(read_only=True)

    class Meta:
        model = Lesson
        fields = ('program', 'title', 'theme', 'theory', 'practice')


class LessonCRUDSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        read_only_fields = ('program', 'editor', 'parent')
        exclude = ('is_approved',)


class LessonsThemeSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True)

    class Meta:
        model = Theme
        fields = ('id', 'program', 'title', 'lessons')


# ----------------------------------------------------------------------------------------------------------------------
# ____________________________________________________Student Block____________________________________________________
# ----------------------------------------------------------------------------------------------------------------------
class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        read_only_fields = ('user',)
        exclude = ('open_program',)


class StudentAccessSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ('user', 'wish_program',)


class StudyingSerializer(serializers.ModelSerializer):
    lesson = LessonShortSerializer(read_only=True)

    class Meta:
        model = Studying
        read_only_fields = ('passed', 'student', 'lesson', 'program')
        fields = '__all__'

