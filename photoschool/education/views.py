from django.db.models import Q
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from reversion.models import Version

from education.models import Program, Theme, Lesson, Student, Studying
from education.serializers import ProgramSerializer, ProgramCRUDSerializer, ThemeCRUDSerializer, LessonCRUDSerializer, \
    StudentSerializer, StudentAccessSerializer, LessonSerializer, StudyingSerializer


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramCRUDSerializer


class ProgramApproveAPIView(APIView):
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
    def get(self, request, pk):
        program = Program.objects.get(pk=pk)
        versions = Version.objects.get_for_object(program)
        history = []
        for version in versions:
            field_dict = version.field_dict
            field_dict['version_id'] = version.id
            field_dict['editor'] = version.revision.user.first_name
            if field_dict['is_approved'] is True:
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


class ProgramLessonsAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer

    def get_queryset(self, **kwargs):
        return Lesson.objects.filter(Q(program__title=self.kwargs.get('program')) & Q(is_approved=True))


class StudyingViewSet(viewsets.ModelViewSet):
    queryset = Studying.objects.all()
    serializer_class = StudyingSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset.all()
        else:
            return self.queryset.filter(student__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user.student)


class ThemeViewSet(viewsets.ModelViewSet):
    queryset = Theme.objects.all()
    serializer_class = ThemeCRUDSerializer


class ThemeApproveAPIView(APIView):
    def get(self, request, pk):
        theme = Theme.objects.get(pk=pk)
        versions = Version.objects.get_for_object(theme)
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
            theme = Theme.objects.get(pk=pk)
            theme.is_approved = True
            theme.program_id = field_dict['program_id']
            theme.title = field_dict['title']
            theme.description = field_dict['description']
            theme.save()
        return Response(ProgramSerializer(theme).data)


class ThemeHistoryRollBackAPIView(APIView):
    def get(self, request, pk):
        theme = Theme.objects.get(pk=pk)
        versions = Version.objects.get_for_object(theme)
        history = []
        for version in versions:
            field_dict = version.field_dict
            field_dict['version_id'] = version.id
            field_dict['editor'] = version.revision.user.first_name
            if field_dict['is_approved'] is True:
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
        return Response(ProgramSerializer(theme).data)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonCRUDSerializer


class LessonApproveAPIView(APIView):
    def get(self, request, pk):
        lesson = Lesson.objects.get(pk=pk)
        versions = Version.objects.get_for_object(lesson)
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
            lesson = Lesson.objects.get(pk=pk)
            lesson.is_approved = True
            lesson.program_id = field_dict['program_id']
            lesson.theme_id = field_dict['theme_id']
            lesson.title = field_dict['title']
            lesson.description = field_dict['description']
            lesson.theory = field_dict['theory']
            lesson.practice = field_dict['practice']
            lesson.answer = field_dict['answer']
            lesson.save()
        return Response(ProgramSerializer(lesson).data)


class LessonHistoryRollBackAPIView(APIView):
    def get(self, request, pk):
        lesson = Lesson.objects.get(pk=pk)
        versions = Version.objects.get_for_object(lesson)
        history = []
        for version in versions:
            field_dict = version.field_dict
            field_dict['version_id'] = version.id
            field_dict['editor'] = version.revision.user.first_name
            if field_dict['is_approved'] is True:
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
        lesson.description = field_dict['description']
        lesson.theory = field_dict['theory']
        lesson.practice = field_dict['practice']
        lesson.answer = field_dict['answer']
        lesson.save()
        return Response(ProgramSerializer(lesson).data)


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StudentAccessViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentAccessSerializer

    http_method_names = ['get', 'patch']

