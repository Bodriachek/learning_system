import pytest
from django.contrib.auth import get_user_model

from model_bakery import baker
from rest_framework.test import APIClient

from photoschool.models import Student, Program, Theme, Lesson, Studying

User = get_user_model()


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        baker.make(
            User, is_superuser=True, username='admin', is_staff=True, email='admin@example.com', first_name='Main admin'
        )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def editor_user():
    return baker.make(User, username='editor', first_name='Editor', email='editor@gmail.com', is_editor=True)


@pytest.fixture
def manager_user():
    return baker.make(User, username='manager', first_name='Manager', email='manager@gmail.com', is_manager=True)


@pytest.fixture
def program_photo():
    return baker.make(Program, is_approved=True, title='Photo', description='About photo')


@pytest.fixture
def program_video():
    return baker.make(Program, is_approved=True, title='Video', description='About video')


@pytest.fixture
def program_not_approve():
    return baker.make(Program, is_approved=False, title='Not', description='description')


@pytest.fixture
def theme_photoshop(program_photo):
    return baker.make(Theme, is_approved=True, program=program_photo, title='Photoshop', description='About photoshop')


@pytest.fixture
def theme_not_approve(program_photo):
    return baker.make(Theme, program=program_photo, title='Theme not', description='not theme')


@pytest.fixture
def lesson_photoshop_retouch(program_photo, editor_user):
    return baker.make(
        Lesson, is_approved=True, program=program_photo, editor=editor_user,
        title='About Photoshop retouch', theory='You can retouch in photoshop',
        practice='What you can do in photoshop?', answer='retouch'
    )


@pytest.fixture
def lesson_lightroom(program_photo, editor_user):
    return baker.make(
        Lesson, is_approved=True, program=program_photo, editor=editor_user,
        title='About Lightroom', theory='The best app for photo processing',
        practice='The best app for photo processing?', answer='lightroom'
    )


@pytest.fixture
def lesson_pixelmator(program_photo, editor_user, theme_photoshop):
    return baker.make(
        Lesson, is_approved=True, program=program_photo, theme=theme_photoshop, editor=editor_user,
        title='Pixelmator', theory='Pixelmator', practice='Pixelmator', answer='Pixelmator'
    )


@pytest.fixture
def lesson_not_approve(program_photo, editor_user):
    return baker.make(
        Lesson, program=program_photo, editor=editor_user,
        title='Lesson not approve', theory='not_approve_lesson',
        practice='not_approve_lesson', answer='answer'
    )


@pytest.fixture
def student_user():
    return baker.make(User, first_name='Student1', email='student1@gmail.com')


@pytest.fixture
def student_user2():
    return baker.make(User, username='student2', first_name='Student2', email='student2@gmail.com')


@pytest.fixture
def student(student_user):
    return baker.make(Student, user=student_user)


@pytest.fixture
def studying(student, lesson_photoshop_retouch):
    student.open_programs.add(lesson_photoshop_retouch.program)
    studying = Studying.objects.get(student=student, lesson=lesson_photoshop_retouch)
    return studying


@pytest.fixture
def studying2(student, lesson_lightroom):
    student.open_programs.add(lesson_lightroom.program)
    studying2 = Studying.objects.get(student=student, lesson=lesson_lightroom)
    studying2.passed = True
    studying2.save()
    return studying2


@pytest.fixture
def studying_signal():
    return baker.make(Studying)

