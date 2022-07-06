from rest_framework import serializers

from .models import *


# ----------------------------------------------------------------------------------------------------------------------
# ____________________________________________________Program Block____________________________________________________
# ----------------------------------------------------------------------------------------------------------------------
class ProgramSerializer(serializers.ModelSerializer):

    class Meta:
        model = Program
        fields = '__all__'


class ProgramShortSerializer(serializers.ModelSerializer):
    student_amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = Program
        read_only_fields = ('title',)
        fields = ('title', 'student_amount')


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
        read_only_fields = ('program',)
        fields = ('id', 'title', 'description')


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


class LessonMicroSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = ('program', 'title', 'theme')


class LessonCRUDSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        read_only_fields = ('program', 'editor', 'parent')
        exclude = ('is_approved',)


class LessonThemeSerializer(serializers.ModelSerializer):
    actual_lesson = serializers.SerializerMethodField()

    def get_actual_lesson(self, obj):
        return obj.lesson.actual_version

    class Meta:
        model = Theme
        fields = ('id', 'program', 'title', 'actual_lesson')


# ----------------------------------------------------------------------------------------------------------------------
# ____________________________________________________Student Block____________________________________________________
# ----------------------------------------------------------------------------------------------------------------------
class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        read_only_fields = ('user',)
        exclude = ('open_program',)


class StudentShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = ('id', 'user')


class StudentAccessSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ('user', 'wish_program')


class StudyingSerializer(serializers.ModelSerializer):
    actual_lesson = serializers.SerializerMethodField()

    def get_actual_lesson(self, obj):
        return obj.lesson.actual_version

    class Meta:
        model = Studying
        read_only_fields = ('id', 'passed', 'student', 'actual_lesson', 'program')
        fields = '__all__'


class StudentLessonsPassedSerializer(serializers.ModelSerializer):
    amount_passed_lesson = serializers.IntegerField(read_only=True)

    class Meta:
        model = Student
        fields = ('user', 'amount_passed_lesson')


class ProgramListSerializer(serializers.ModelSerializer):
    themes = ThemeCRUDSerializer(many=True, read_only=True)
    lessons = LessonMicroSerializer(many=True, read_only=True)

    class Meta:
        model = Program
        fields = '__all__'
