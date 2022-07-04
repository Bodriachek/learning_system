import pytest
from reversion.models import Version
import json
from model_bakery import baker
from rest_framework import status
from django.contrib.auth import get_user_model

from photoschool.models import Program, Theme, Lesson

pytestmark = pytest.mark.django_db

User = get_user_model()


def test_add_program(api_client, editor_user):
    api_client.force_login(editor_user)

    resp = api_client.post('/api/v1/program/', {
        "title": "Video",
        "description": 'About video'
    })

    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.data

    assert 'id' in data
    del data['id']

    assert data == {
        "title": "Video",
        "description": "About video"
    }


def test_add_theme(api_client, editor_user, program_photo):
    api_client.force_login(editor_user)

    resp = api_client.post(f'/api/v1/theme/{program_photo.pk}/', {
        'program': program_photo,
        "title": "lightroom",
        "description": 'About lightroom'
    })

    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.data

    assert 'id' in data
    del data['id']
    assert data == {
        "title": "lightroom",
        "description": 'About lightroom'
    }


def test_add_lesson(api_client, editor_user, program_photo, theme_photoshop):
    api_client.force_login(editor_user)

    resp = api_client.post(f'/api/v1/lesson/{program_photo.pk}/', {
        'theme': theme_photoshop.pk,
        "title": "PL1",
        "theory": 'About photoshop',
        'practice': 'photoshop',
        'answer': 'photoshop'
    })
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.data

    assert 'id' in data
    del data['id']

    assert data == {
        "title": "PL1",
        "theory": 'About photoshop',
        'practice': 'photoshop',
        'answer': 'photoshop',
        "parent": None,
        "editor": editor_user.pk,
        'theme': theme_photoshop.pk,
        'program': str(program_photo.pk),
    }


def test_program_approve(api_client, editor_user, manager_user):

    api_client.force_login(editor_user)

    resp = api_client.post('/api/v1/program/', {
        'title': 'Test approve v1',
        'description': 'Test approve description v1'
    })

    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.data

    assert 'id' in data
    program_id = data['id']
    program = Program.objects.get(id=program_id)

    api_client.logout()
    api_client.force_login(manager_user)

    resp = api_client.put(
        f'/api/v1/program-approve/{program.id}/', dict(
            version_id=1, approved=True
        )
    )

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert 'id' in data
    del data['id']

    assert data == {
        "is_approved": True,
        "title": "Test approve v1",
        "description": "Test approve description v1"
    }


def test_theme_approve(api_client, editor_user, manager_user, program_photo):

    api_client.force_login(editor_user)

    resp = api_client.post(f'/api/v1/theme/{program_photo.pk}/', {
        'title': 'Test approve v1',
        'description': 'Test approve description v1'
    })

    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.data

    assert 'id' in data
    theme_id = data['id']
    theme = Theme.objects.get(id=theme_id)

    api_client.logout()
    api_client.force_login(manager_user)

    resp = api_client.put(
        f'/api/v1/theme-approve/{theme.id}/', dict(
            version_id=1, approved=True
        )
    )

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert 'id' in data
    del data['id']

    assert data == {
        "is_approved": True,
        "title": "Test approve v1",
        "description": "Test approve description v1"
    }


def test_lesson_approve(api_client, editor_user, manager_user, program_photo, theme_photoshop):

    api_client.force_login(editor_user)

    resp = api_client.post(f'/api/v1/lesson/{program_photo.pk}/', {
        'theme': theme_photoshop.pk,
        "title": "PL1",
        "theory": 'About photoshop',
        'practice': 'photoshop',
        'answer': 'photoshop'
    })

    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.data
    assert 'id' in data
    lesson_id = data['id']
    lesson = Lesson.objects.get(id=lesson_id)

    api_client.logout()
    api_client.force_login(manager_user)

    resp = api_client.put(
        f'/api/v1/lesson-approve/{lesson.id}/', dict(
            version_id=1, approved=True
        )
    )

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert 'id' in data
    del data['id']

    assert data == {
        "parent": None,
        "is_approved": True,
        "editor": editor_user.pk,
        'theme': theme_photoshop.pk,
        "title": "PL1",
        "program": program_photo.pk,
        "theory": 'About photoshop',
        'practice': 'photoshop',
        'answer': 'photoshop'
    }

