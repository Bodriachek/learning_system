import pytest
import json
from model_bakery import baker
from rest_framework import status
from django.contrib.auth import get_user_model

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

    resp = api_client.post('/api/v1/theme/1/', {
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

    resp = api_client.post('/api/v1/lesson/1/', {
        'program': program_photo,
        'theme': theme_photoshop,
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
        "editor": editor_user.id,
        'theme': theme_photoshop.id,
        'program': program_photo.id,
    }
