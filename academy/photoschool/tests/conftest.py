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
            User, is_superuser=True, is_staff=True, username='', email='admin@example.com', first_name='Main admin'
        )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def editor_user():
    return baker.make(User, first_name='Editor', email='editor@gmail.com', is_editor=True)


@pytest.fixture
def manager_user():
    return baker.make(User, first_name='Manager', email='manager@gmail.com', is_manager=True)


@pytest.fixture
def program_photo():
    return baker.make(Program, is_approved=True, title='Photo', description='About photo')


@pytest.fixture
def theme_photoshop(program_photo):
    return baker.make(Theme, program=program_photo, title='Photoshop', description='About photoshop')


@pytest.fixture
def lesson_photoshop_retouch(program_photo, theme_photoshop, editor_user):
    return baker.make(
        Lesson, program=program_photo, theme=None, editor=editor_user,
        title='About Photoshop retouch', theory='You can retouch in photoshop',
        practice='What you can do in photoshop?', answer='retouch')


@pytest.fixture
def student_user():
    return baker.make(User, first_name='Student1', email='student1@gmail.com')


@pytest.fixture
def student1(student_user, program_photo):
    return baker.make(Student, user=student_user.id, open_program=program_photo.id)


@pytest.fixture
def studying(student1, lesson_photoshop_retouch):
    return baker.make(Studying, student=student1, lesson=lesson_photoshop_retouch)

