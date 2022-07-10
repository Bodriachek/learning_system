import pytest
import reversion
from reversion.models import Version
import json
from model_bakery import baker
from rest_framework import status
from django.contrib.auth import get_user_model

from photoschool.models import Theme, Lesson, Program

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


def test_update_program(api_client, editor_user):
    api_client.force_login(editor_user)

    resp = api_client.post('/api/v1/program/', {
        "title": "Video",
        "description": 'About video'
    })

    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.data

    assert 'id' in data
    program_id = data['id']
    program = Program.objects.get(id=program_id)
    del data['id']

    assert data == {
        "title": "Video",
        "description": "About video"
    }

    resp = api_client.patch(
        f'/api/v1/program/{program.id}/', dict(
            title="Video v2", description="About video v2"
        )
    )

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert 'id' in data
    del data['id']

    assert data == {
        "title": "Video v2",
        "description": "About video v2"
    }


def test_program_list(api_client, program_photo, program_video, student_user, editor_user):
    program_photo.title = program_photo.title + ' v2'
    program_photo.is_approved = True
    with reversion.create_revision():
        reversion.set_user(editor_user)
        program_photo.save()

    program_video.title = program_video.title + ' v2'
    program_video.is_approved = True
    with reversion.create_revision():
        reversion.set_user(editor_user)
        program_video.save()

    api_client.force_login(student_user)

    resp = api_client.get(
        '/api/v1/program-list/',
        content_type='application/json'
    )

    assert resp.status_code == status.HTTP_200_OK
    data = json.loads(json.dumps(resp.data))

    for item in data:
        assert 'id' in item
        del item['id']
        assert 'editor' in item
        del item['editor']

    assert data == [
        {
            "description": 'About photo',
            "is_approved": True,
            "title": 'Photo v2'
        },
        {
            "description": 'About video',
            "is_approved": True,
            "title": 'Video v2'
        },
    ]


def test_lesson_list(api_client, program_photo, lesson_photoshop_retouch, lesson_lightroom, manager_user, editor_user):
    lesson_photoshop_retouch.title = lesson_photoshop_retouch.title + ' v2'
    lesson_photoshop_retouch.is_approved = True
    with reversion.create_revision():
        reversion.set_user(editor_user)
        lesson_photoshop_retouch.save()

    lesson_lightroom.title = lesson_lightroom.title + ' v2'
    lesson_lightroom.is_approved = True
    with reversion.create_revision():
        reversion.set_user(editor_user)
        lesson_lightroom.save()

    api_client.force_login(manager_user)

    resp = api_client.get(
        f'/api/v1/lesson-list/{program_photo.pk}/',
        content_type='application/json'
    )

    assert resp.status_code == status.HTTP_200_OK
    data = json.loads(json.dumps(resp.data))

    for item in data:
        assert 'id' in item
        del item['id']
        assert 'editor' in item
        del item['editor']
        assert 'version_id' in item
        del item['version_id']

    assert data == [
        {
            "is_approved": True,
            "title": "About Photoshop retouch v2",
            "theory": 'You can retouch in photoshop',
            'practice': 'What you can do in photoshop?',
            'answer': 'retouch',
            "parent_id": None,
            "editor_id": editor_user.pk,
            'theme_id': None,
            'program_id': program_photo.pk,
        },
        {
            "is_approved": True,
            "title": "About Lightroom v2",
            "theory": 'The best app for photo processing',
            'practice': 'The best app for photo processing?',
            'answer': 'lightroom',
            "parent_id": lesson_photoshop_retouch.pk,
            "editor_id": editor_user.pk,
            'theme_id': None,
            'program_id': program_photo.pk,
        },
    ]


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


def test_update_theme(api_client, editor_user, program_photo):
    api_client.force_login(editor_user)

    resp = api_client.post(f'/api/v1/theme/{program_photo.pk}/', {
        'program': program_photo,
        "title": "lightroom",
        "description": 'About lightroom'
    })

    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.data

    assert 'id' in data
    theme_id = data['id']
    theme = Theme.objects.get(id=theme_id)
    del data['id']

    assert data == {
        "title": "lightroom",
        "description": 'About lightroom'
    }

    resp = api_client.patch(
        f'/api/v1/theme/{program_photo.pk}/{theme.id}/', dict(
            title="lightroom v2", description="About lightroom v2"
        )
    )

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert 'id' in data
    del data['id']

    assert data == {
        "title": "lightroom v2",
        "description": 'About lightroom v2'
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


def test_update_lesson(api_client, editor_user, program_photo, theme_photoshop):
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

    resp = api_client.patch(
        f'/api/v1/lesson/{program_photo.pk}/{lesson_id}/', dict(
            title="PL1 v2", theory="About photoshop v2", practice="photoshop v2"
        )
    )

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert 'id' in data
    del data['id']

    assert data == {
        "title": "PL1 v2",
        "theory": 'About photoshop v2',
        'practice': 'photoshop v2',
        'answer': 'photoshop',
        "parent": None,
        "editor": editor_user.pk,
        'theme': theme_photoshop.pk,
        'program': program_photo.pk,
    }


def test_new_program_approve(api_client, editor_user, manager_user):
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


def test_new_versions_program_approve(api_client, editor_user, manager_user, program_photo):

    program_photo.title = program_photo.title + ' v1'
    with reversion.create_revision():
        reversion.set_user(editor_user)
        program_photo.save()

    program_photo.title = program_photo.title + ' v2'
    with reversion.create_revision():
        reversion.set_user(editor_user)
        program_photo.save()

    api_client.force_login(manager_user)

    resp = api_client.put(
        f'/api/v1/program-approve/{program_photo.pk}/', dict(
            version_id=1, approved=True
        )
    )

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert 'id' in data
    del data['id']

    assert data == {
        "is_approved": True,
        "title": 'Photo v1',
        "description": 'About photo'
    }


def test_program_approve_get(api_client, program_photo, manager_user, editor_user):
    program_photo.title = program_photo.title + ' v1'
    program_photo.is_approved = True
    with reversion.create_revision():
        reversion.set_user(editor_user)
        program_photo.save()

    api_client.force_login(manager_user)

    resp = api_client.get(f'/api/v1/program-approve/{program_photo.pk}/')

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert 'id' in data['published']
    del data['published']['id']

    assert data == {
        "published": {
            "editor": 'Editor',
            "description": "About photo",
            "is_approved": True,
            "title": "Photo v1",
            "version_id": 1
        },
        "not_approved": []
    }


def test_program_not_approve_get(api_client, program_not_approve, manager_user, editor_user):
    program_not_approve.title = program_not_approve.title + ' v1'
    with reversion.create_revision():
        reversion.set_user(editor_user)
        program_not_approve.save()

    api_client.force_login(manager_user)

    resp = api_client.get(f'/api/v1/program-approve/{program_not_approve.pk}/')

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    # assert 'id' in data['not_approved']
    # del data['not_approved']['id']

    assert data == {
        "not_approved": [
            {
                "editor": 'Editor',
                "description": "description",
                "is_approved": False,
                "title": "Not v1",
                "id": 1,
                "version_id": 1
            }
        ]
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
        "description": "Test approve description v1",
        "program": program_photo.id
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


def test_program_rollback(api_client, editor_user, manager_user, program_photo):

    program_photo.title = program_photo.title + ' v1'
    program_photo.is_approved = True
    with reversion.create_revision():
        reversion.set_user(editor_user)
        program_photo.save()

    program_photo.title = program_photo.title + ' v2'
    program_photo.is_approved = True
    with reversion.create_revision():
        reversion.set_user(editor_user)
        program_photo.save()

    api_client.force_login(manager_user)

    resp = api_client.put(
        f'/api/v1/program-history/{program_photo.pk}/', dict(
            version_id=1
        )
    )

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert 'id' in data
    del data['id']

    assert data == {
        "is_approved": True,
        "title": 'Photo v1',
        "description": "About photo"
    }

    resp = api_client.get(f'/api/v1/program-history/{program_photo.pk}/')

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    for item in data:
        assert 'id' in item
        del item['id']
        assert 'editor' in item
        del item['editor']

    assert data == [{
            "is_approved": True,
            "title": 'Photo v1',
            'version_id': 3,
            "description": "About photo"
        },
        {
        "is_approved": True,
        "title": 'Photo v1 v2',
        'version_id': 2,
        "description": "About photo"
        },
        {
            "is_approved": True,
            "title": 'Photo v1',
            'version_id': 1,
            "description": "About photo"
        }
    ]


def test_theme_rollback(api_client, editor_user, manager_user, program_photo, theme_photoshop):

    theme_photoshop.title = theme_photoshop.title + ' v1'
    theme_photoshop.is_approved = True
    with reversion.create_revision():
        reversion.set_user(editor_user)
        theme_photoshop.save()

    theme_photoshop.title = theme_photoshop.title + ' v2'
    theme_photoshop.is_approved = True
    with reversion.create_revision():
        reversion.set_user(editor_user)
        theme_photoshop.save()

    api_client.force_login(manager_user)

    resp = api_client.put(
        f'/api/v1/theme-history/{theme_photoshop.pk}/', dict(
            version_id=1
        )
    )

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert 'id' in data
    del data['id']

    assert data == {
        "is_approved": True,
        "title": 'Photoshop v1',
        "description": "About photoshop",
        "program": program_photo.id
    }


def test_lesson_rollback(api_client, editor_user, manager_user, program_photo, lesson_photoshop_retouch):

    lesson_photoshop_retouch.title = lesson_photoshop_retouch.title + ' v1'
    lesson_photoshop_retouch.is_approved = True
    with reversion.create_revision():
        reversion.set_user(editor_user)
        lesson_photoshop_retouch.save()

    lesson_photoshop_retouch.title = lesson_photoshop_retouch.title + ' v2'
    lesson_photoshop_retouch.is_approved = True
    with reversion.create_revision():
        reversion.set_user(editor_user)
        lesson_photoshop_retouch.save()

    api_client.force_login(manager_user)

    resp = api_client.put(
        f'/api/v1/lesson-history/{lesson_photoshop_retouch.pk}/', dict(
            version_id=1
        )
    )

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert 'id' in data
    del data['id']

    assert data == {
        "is_approved": True,
        "title": "About Photoshop retouch v1",
        "theory": 'You can retouch in photoshop',
        'practice': 'What you can do in photoshop?',
        'answer': 'retouch',
        "parent": None,
        "editor": editor_user.pk,
        'theme': None,
        'program': program_photo.pk
    }


def test_studying(api_client, student1, student_user, studying, lesson_photoshop_retouch, editor_user, program_photo):

    lesson_photoshop_retouch.title = lesson_photoshop_retouch.title + 'a'
    lesson_photoshop_retouch.is_approved = True
    with reversion.create_revision():
        reversion.set_user(editor_user)
        lesson_photoshop_retouch.save()

    api_client.force_login(student_user)

    resp = api_client.patch(f'/api/v1/studying/{studying.pk}/', {
        "id": studying.id,
        "actual_lesson": {
            "id": lesson_photoshop_retouch.id,
            "parent_id": None,
            "is_approved": True,
            "editor_id": editor_user.id,
            "title": lesson_photoshop_retouch.title,
            "program_id": program_photo.id,
            "theme_id": None,
            "theory": lesson_photoshop_retouch.theory,
            "practice": lesson_photoshop_retouch.practice,
            "answer": lesson_photoshop_retouch.answer,
            "editor": editor_user.username
        },
        "answer": "retouch",
        "passed": False,
        "lesson": lesson_photoshop_retouch.id,
        "student": student1.id
    }, format="json")

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert 'id' in data
    del data['id']

    assert data == {
        "actual_lesson": {
            "id": lesson_photoshop_retouch.id,
            "parent_id": None,
            "is_approved": True,
            "editor_id": editor_user.id,
            "title": lesson_photoshop_retouch.title,
            "program_id": program_photo.id,
            "theme_id": None,
            "theory": lesson_photoshop_retouch.theory,
            "practice": lesson_photoshop_retouch.practice,
            "answer": lesson_photoshop_retouch.answer,
            "editor": editor_user.username
        },
        "answer": "retouch",
        "passed": True,
        "lesson": lesson_photoshop_retouch.id,
        "student": student1.id
    }
# --------------------------------------------- PERMISSIONS ---------------------------------------------


def test_program_crud_permission(api_client, student_user):
    api_client.force_login(student_user)

    resp = api_client.get('/api/v1/program/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_theme_crud_permission(api_client, student_user, program_photo):
    api_client.force_login(student_user)

    resp = api_client.get(f'/api/v1/theme/{program_photo.pk}/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_lesson_crud_permission(api_client, student_user, program_photo):
    api_client.force_login(student_user)

    resp = api_client.get(f'/api/v1/lesson/{program_photo.pk}/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_program_approve_student_login_permission(api_client, student_user, program_photo):
    api_client.force_login(student_user)

    resp = api_client.get(f'/api/v1/program-approve/{program_photo.pk}/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_program_approve_editor_login_permission(api_client, editor_user, program_photo):
    api_client.force_login(editor_user)

    resp = api_client.get(f'/api/v1/program-approve/{program_photo.pk}/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_theme_approve_student_login_permission(api_client, student_user, theme_photoshop):
    api_client.force_login(student_user)

    resp = api_client.get(f'/api/v1/theme-approve/{theme_photoshop.pk}/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_theme_approve_editor_login_permission(api_client, editor_user, theme_photoshop):
    api_client.force_login(editor_user)

    resp = api_client.get(f'/api/v1/theme-approve/{theme_photoshop.pk}/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_lesson_approve_student_login_permission(api_client, student_user, lesson_photoshop_retouch):
    api_client.force_login(student_user)

    resp = api_client.get(f'/api/v1/lesson-approve/{lesson_photoshop_retouch.pk}/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_lesson_approve_editor_login_permission(api_client, editor_user, lesson_photoshop_retouch):
    api_client.force_login(editor_user)

    resp = api_client.get(f'/api/v1/lesson-approve/{lesson_photoshop_retouch.pk}/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_program_history_student_login_permission(api_client, student_user, program_photo):
    api_client.force_login(student_user)

    resp = api_client.get(f'/api/v1/program-history/{program_photo.pk}/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_program_history_editor_login_permission(api_client, editor_user, program_photo):
    api_client.force_login(editor_user)

    resp = api_client.get(f'/api/v1/program-history/{program_photo.pk}/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_theme_history_student_login_permission(api_client, student_user, theme_photoshop):
    api_client.force_login(student_user)

    resp = api_client.get(f'/api/v1/theme-history/{theme_photoshop.pk}/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_theme_history_editor_login_permission(api_client, editor_user, theme_photoshop):
    api_client.force_login(editor_user)

    resp = api_client.get(f'/api/v1/theme-history/{theme_photoshop.pk}/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_lesson_history_student_login_permission(api_client, student_user, lesson_photoshop_retouch):
    api_client.force_login(student_user)

    resp = api_client.get(f'/api/v1/lesson-history/{lesson_photoshop_retouch.pk}/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_lesson_history_editor_login_permission(api_client, editor_user, lesson_photoshop_retouch):
    api_client.force_login(editor_user)

    resp = api_client.get(f'/api/v1/lesson-history/{lesson_photoshop_retouch.pk}/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_program_student_amount_student_login_permission(api_client, student_user):
    api_client.force_login(student_user)

    resp = api_client.get('/api/v1/program-students-amount/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_program_student_amount_editor_login_permission(api_client, editor_user):
    api_client.force_login(editor_user)

    resp = api_client.get('/api/v1/program-students-amount/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_lesson_list_staff_permission(api_client, student_user, program_photo):
    api_client.force_login(student_user)

    resp = api_client.get(f'/api/v1/lesson-list/{program_photo.pk}/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_lesson_for_approve_editor_login_permission(api_client, editor_user):
    api_client.force_login(editor_user)

    resp = api_client.get('/api/v1/lesson-approve-list/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_lesson_theme_list_staff_permission(api_client, student_user, program_photo):
    api_client.force_login(student_user)

    resp = api_client.get(f'/api/v1/lesson-theme/{program_photo.pk}/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_lesson_editor_list_staff_permission(api_client, student_user, program_photo, editor_user):
    api_client.force_login(student_user)

    resp = api_client.get(f'/api/v1/lesson-editor/{program_photo.pk}/{editor_user.pk}/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_student_access_editor_login_permission(api_client, editor_user):
    api_client.force_login(editor_user)

    resp = api_client.get('/api/v1/student-access/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_student_access_student_login_permission(api_client, student_user):
    api_client.force_login(student_user)

    resp = api_client.get('/api/v1/student-access/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_studying_editor_login_permission(api_client, editor_user):
    api_client.force_login(editor_user)

    resp = api_client.get('/api/v1/studying/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_studying_manager_login_permission(api_client, manager_user):
    api_client.force_login(manager_user)

    resp = api_client.get('/api/v1/studying/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_students_lesson_passed_manager_login_permission(api_client, manager_user):
    api_client.force_login(manager_user)

    resp = api_client.get('/api/v1/students-lesson-passed/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_students_lesson_passed_editor_login_permission(api_client, editor_user):
    api_client.force_login(editor_user)

    resp = api_client.get('/api/v1/students-lesson-passed/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_superuser_editor_login_permission(api_client, editor_user):
    api_client.force_login(editor_user)

    resp = api_client.get('/api/v1/users/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_superuser_manager_login_permission(api_client, manager_user):
    api_client.force_login(manager_user)

    resp = api_client.get('/api/v1/users/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_superuser_student_login_permission(api_client, student_user):
    api_client.force_login(student_user)

    resp = api_client.get('/api/v1/users/')

    assert resp.status_code == status.HTTP_403_FORBIDDEN
