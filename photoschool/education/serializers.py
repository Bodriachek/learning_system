from rest_framework import serializers

from education.models import *


class ProgramSerializer(serializers.ModelSerializer):

    class Meta:
        model = Program
        fields = '__all__'


class ProgramCRUDSerializer(serializers.ModelSerializer):

    class Meta:
        model = Program
        fields = ('id', 'title', 'description')


class ThemeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Theme
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = '__all__'


class ThemeCRUDSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True)

    class Meta:
        model = Theme
        fields = ('id', 'program', 'title', 'description', 'lessons')


class LessonCRUDSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        exclude = ('is_approved',)


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

    class Meta:
        model = Studying
        read_only_fields = ('passed', 'student', 'lesson')
        fields = '__all__'

