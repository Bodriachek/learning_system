from django.db.models import When, Count, Case
from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from reversion.models import Version

from .models import Program, Theme, Lesson, Student, Studying
from .permissions import (
    IsStudentPermission, IsStudyingOwnerPermission, IsStaffPermission,
    IsManagerOrSuperUserPermission
)
from .serializers import (
    ProgramSerializer, ProgramCRUDSerializer, ThemeCRUDSerializer, LessonCRUDSerializer,
    StudentSerializer, StudentAccessSerializer, LessonSerializer, StudyingSerializer, LessonsThemeSerializer,
    StudentShortSerializer, StudentLessonsPassedSerializer, ProgramShortSerializer, LessonMicroSerializer,
    ProgramListSerializer, ThemeSerializer
)


# ----------------------------------------------------------------------------------------------------------------------
# ____________________________________________________Program Block____________________________________________________
# ----------------------------------------------------------------------------------------------------------------------
class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    permission_classes = [IsStaffPermission]
    serializer_class = ProgramCRUDSerializer


class ProgramApproveAPIView(APIView):
    permission_classes = [IsManagerOrSuperUserPermission]

    def get(self, request, pk):
        program = Program.objects.get(pk=pk)
        versions = Version.objects.get_for_object(program)
        not_approved = []

        for version in versions:
            field_dict = version.field_dict
            field_dict['version_id'] = version.id
            field_dict['editor'] = version.revision.user.first_name
            if field_dict['is_approved'] is False:
                not_approved.append(field_dict)
            else:
                return Response({'published': field_dict, 'not_approved': not_approved})
        return Response({'not_approved': not_approved})

    def put(self, request, pk):
        data = request.data
        version_id = data["version_id"]
        work_version = Version.objects.get(pk=version_id)
        field_dict = work_version.field_dict
        if data['approved'] is False:
            work_version.delete()
        else:
            program = Program.objects.get(pk=pk)
            program.is_approved = True
            program.title = field_dict['title']
            program.description = field_dict['description']
            program.save()
        return Response(ProgramSerializer(program).data)


class ProgramHistoryRollBackAPIView(APIView):
    permission_classes = [IsManagerOrSuperUserPermission]

    def get(self, request, pk):
        program = Program.objects.get(pk=pk)
        versions = Version.objects.get_for_object(program)
        history = []
        for version in versions:
            field_dict = version.field_dict
            field_dict['version_id'] = version.id
            field_dict['editor'] = version.revision.user.username
            if field_dict['is_approved']:
                history.append(field_dict)

        return Response(history)

    def put(self, request, pk):
        data = request.data
        version_id = data["version_id"]
        work_version = Version.objects.get(pk=version_id)
        field_dict = work_version.field_dict
        program = Program.objects.get(pk=pk)
        program.is_approved = True
        program.title = field_dict['title']
        program.description = field_dict['description']
        program.save()
        return Response(ProgramSerializer(program).data)


class ProgramStudentsAmountListAPIView(generics.ListAPIView):
    serializer_class = ProgramShortSerializer
    permission_classes = [IsManagerOrSuperUserPermission]
    queryset = Program.objects.annotate(student_amount=Count('students'))


class ProgramListAPIView(generics.ListAPIView):
    serializer_class = ProgramListSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Program.objects.prefetch_related('themes', 'lessons').filter(is_approved=True)


# ----------------------------------------------------------------------------------------------------------------------
# _____________________________________________________Theme Block_____________________________________________________
# ----------------------------------------------------------------------------------------------------------------------
class ThemeViewSet(viewsets.ModelViewSet):
    queryset = Theme.objects.all()
    permission_classes = [IsStaffPermission]
    serializer_class = ThemeCRUDSerializer

    def get_queryset(self):
        program_id = self.kwargs['program_id']
        return self.queryset.filter(program_id=program_id, is_approved=True)

    def perform_create(self, serializer):
        program_id = self.kwargs['program_id']
        serializer.save(program_id=program_id)


class ThemeApproveAPIView(APIView):
    permission_classes = [IsManagerOrSuperUserPermission]

    def get(self, request, pk):
        theme = Theme.objects.get(pk=pk)
        versions = Version.objects.get_for_object(theme)
        not_approved = []

        for version in versions:
            field_dict = version.field_dict
            field_dict['version_id'] = version.id
            field_dict['editor'] = version.revision.user.username
            if field_dict['is_approved'] is False:
                not_approved.append(field_dict)
            else:
                return Response({'published': field_dict, 'not_approved': not_approved})
        return Response({'not_approved': not_approved})

    def put(self, request, pk):
        data = request.data
        version_id = data["version_id"]
        work_version = Version.objects.get(pk=version_id)
        field_dict = work_version.field_dict
        if data['approved'] is False:
            work_version.delete()
        else:
            theme = Theme.objects.get(pk=pk)
            theme.is_approved = True
            theme.program_id = field_dict['program_id']
            theme.title = field_dict['title']
            theme.description = field_dict['description']
            theme.save()
        return Response(ThemeSerializer(theme).data)


class ThemeHistoryRollBackAPIView(APIView):
    permission_classes = [IsManagerOrSuperUserPermission]

    def get(self, request, pk):
        theme = Theme.objects.get(pk=pk)
        versions = Version.objects.get_for_object(theme)
        history = []
        for version in versions:
            field_dict = version.field_dict
            field_dict['version_id'] = version.id
            field_dict['editor'] = version.revision.user.username
            if field_dict['is_approved']:
                history.append(field_dict)

        return Response(history)

    def put(self, request, pk):
        data = request.data
        version_id = data["version_id"]
        work_version = Version.objects.get(pk=version_id)
        field_dict = work_version.field_dict
        theme = Theme.objects.get(pk=pk)
        theme.is_approved = True
        theme.program_id = field_dict['program_id']
        theme.title = field_dict['title']
        theme.description = field_dict['description']
        theme.save()
        return Response(ThemeSerializer(theme).data)


# ----------------------------------------------------------------------------------------------------------------------
# _____________________________________________________Lesson Block_____________________________________________________
# ----------------------------------------------------------------------------------------------------------------------
class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    permission_classes = [IsStaffPermission]
    serializer_class = LessonCRUDSerializer

    def get_queryset(self):
        program_id = self.kwargs['program_id']
        return self.queryset.filter(program_id=program_id, is_approved=True)

    def perform_create(self, serializer):
        program_id = self.kwargs['program_id']
        serializer.save(editor=self.request.user, program_id=program_id)

    def perform_update(self, serializer):
        serializer.save(editor=self.request.user)


class LessonForApproveListAPIView(generics.ListAPIView):
    queryset = Lesson.objects.filter(is_approved=False)
    permission_classes = [IsManagerOrSuperUserPermission]
    serializer_class = LessonSerializer


class LessonApproveAPIView(APIView):
    permission_classes = [IsManagerOrSuperUserPermission]

    def get(self, request, pk):
        lesson = Lesson.objects.get(pk=pk)
        versions = Version.objects.get_for_object(lesson)
        not_approved = []

        for version in versions:
            field_dict = version.field_dict
            field_dict['version_id'] = version.id
            field_dict['editor'] = version.revision.user.username
            if field_dict['is_approved'] is False:
                not_approved.append(field_dict)
            else:
                return Response({'published': field_dict, 'not_approved': not_approved})
        return Response({'not_approved': not_approved})

    def put(self, request, pk):
        data = request.data
        version_id = data["version_id"]
        work_version = Version.objects.get(pk=version_id)
        field_dict = work_version.field_dict
        if data['approved'] is False:
            work_version.delete()
        else:
            lesson = Lesson.objects.get(pk=pk)
            lesson.is_approved = True
            lesson.program_id = field_dict['program_id']
            lesson.theme_id = field_dict['theme_id']
            lesson.title = field_dict['title']
            lesson.theory = field_dict['theory']
            lesson.practice = field_dict['practice']
            lesson.answer = field_dict['answer']
            lesson.save()
        return Response(LessonSerializer(lesson).data)


class LessonHistoryRollBackAPIView(APIView):
    permission_classes = [IsManagerOrSuperUserPermission]

    def get(self, request, pk):
        lesson = Lesson.objects.get(pk=pk)
        versions = Version.objects.get_for_object(lesson)
        history = []
        for version in versions:
            field_dict = version.field_dict
            field_dict['version_id'] = version.id
            field_dict['editor'] = version.revision.user.username
            if field_dict['is_approved']:
                history.append(field_dict)

        return Response(history)

    def put(self, request, pk):
        data = request.data
        version_id = data["version_id"]
        work_version = Version.objects.get(pk=version_id)
        field_dict = work_version.field_dict
        lesson = Lesson.objects.get(pk=pk)
        lesson.is_approved = True
        lesson.program_id = field_dict['program_id']
        lesson.theme_id = field_dict['theme_id']
        lesson.title = field_dict['title']
        lesson.theory = field_dict['theory']
        lesson.practice = field_dict['practice']
        lesson.answer = field_dict['answer']
        lesson.save()
        return Response(LessonSerializer(lesson).data)


class LessonsThemeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, **kwargs):
        filter_dict = dict(program__title=self.kwargs.get('program_id'), is_approved=True)
        themes = Theme.objects.filter(**filter_dict).prefetch_related('lessons')
        lessons = Lesson.objects.filter(**filter_dict).select_related('theme')
        without_theme = []

        for lesson in lessons:
            if lesson.theme is None:
                without_theme.append(lesson)

        return Response({'with_theme': LessonsThemeSerializer(themes, many=True).data,
                         'without_theme': LessonMicroSerializer(without_theme, many=True).data})


class LessonEditorListAPIView(generics.ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonCRUDSerializer
    permission_classes = [IsManagerOrSuperUserPermission]

    def get_queryset(self):
        editor_id = self.kwargs['editor_id']
        return self.queryset.filter(program_id=self.kwargs.get('program_id'),
                                    editor_id=editor_id, is_approved=True)


# ----------------------------------------------------------------------------------------------------------------------
# ____________________________________________________Student Block____________________________________________________
# ----------------------------------------------------------------------------------------------------------------------
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsStudentPermission]

    def get_queryset(self, **kwargs):
        if self.request.user.is_superuser:
            return self.queryset.all()
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StudentAccessViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentAccessSerializer
    permission_classes = [IsManagerOrSuperUserPermission]

    http_method_names = ['get', 'patch']


class StudyingViewSet(viewsets.ModelViewSet):
    queryset = Studying.objects.select_related('lesson')
    serializer_class = StudyingSerializer
    permission_classes = [IsStudyingOwnerPermission]
    http_method_names = ['get', 'retrieve', 'patch']

    def get_queryset(self, **kwargs):
        if self.request.user.is_superuser:
            return self.queryset.filter(passed=False)
        return self.queryset.filter(student__user=self.request.user, passed=False)


class AvailableLessonProgramListAPIView(generics.ListAPIView):
    queryset = Studying.objects.select_related('lesson')
    serializer_class = StudyingSerializer
    permission_classes = [IsStudyingOwnerPermission]

    def get_queryset(self, **kwargs):
        return self.queryset.filter(lesson__program_id=self.kwargs.get('program_id'),
                                    student__user=self.request.user)


class StudentLessonsPassedListAPIIView(generics.ListAPIView):
    queryset = Student.objects.annotate(amount_passed_lesson=Count(Case(When(studying__passed=True, then=1))))
    serializer_class = StudentLessonsPassedSerializer
    permission_classes = [IsStudentPermission]


class StudentProgramSubscribedListAPIIView(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentShortSerializer
    permission_classes = [IsManagerOrSuperUserPermission]

    def get_queryset(self, **kwargs):
        return self.queryset.filter(open_program=self.kwargs['program_id'])

