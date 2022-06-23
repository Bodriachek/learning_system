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
        "id": 3,
        "title": "Motion graphics",
        "description": "About motion graphics"
    }

