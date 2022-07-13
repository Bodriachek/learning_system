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


def test_add_student(api_client, student_user2, program_photo):
    api_client.force_login(student_user2)

    resp = api_client.post('/api/v1/student/', {
        "wish_programs": program_photo.id
    })

    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.data

    assert 'id' in data
    student_id = data['id']
    del data['id']

    assert data == {
        "user": student_user2.id,
        "wish_programs": [
            program_photo.id
        ]
    }

    resp = api_client.get('/api/v1/student/')

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert data == [{
        'id': student_id,
        "user": student_user2.id,
        "wish_programs": [
            program_photo.id
        ]
    }]


# @pytest.mark.skip
def test_create_studying_signal(
    api_client, student, student_user, manager_user, program_photo,
    lesson_pixelmator, studying_signal, 
):
    from photoschool.models import Studying
    api_client.force_login(manager_user)

    studying_count = Studying.objects.count()

    resp = api_client.patch(f'/api/v1/student-access/{student.id}/', {
        "open_programs": [program_photo.id]
    }, format="json")

    assert resp.status_code == status.HTTP_200_OK

    assert studying_count + 1 == Studying.objects.count()

    resp = api_client.patch(f'/api/v1/student-access/{student.id}/', {
        "open_programs": []
    }, format="json")

    assert resp.status_code == status.HTTP_200_OK

    assert studying_count == Studying.objects.count()


def test_student_list_superuser(api_client, student):
    admin = User.objects.get(username='admin')
    api_client.force_login(admin)
    
    resp = api_client.get('/api/v1/student/')

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert data == [{
        'id': student.id,
        "user": student.user_id,
        "wish_programs": []
    }]


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


def test_update_program(api_client, editor_user, program_photo):
    api_client.force_login(editor_user)

    resp = api_client.put(
        f'/api/v1/program/{program_photo.pk}/', dict(
            title="Photo v2", description="About photo v2"
        )
    )

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert data == {
        "id": program_photo.id,
        "title": "Photo v2",
        "description": "About photo v2"
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

    assert data == [
        {
            'id': program_photo.id,
            "description": 'About photo',
            "is_approved": True,
            "title": 'Photo v2',
            'editor': editor_user.username
        },
        {
            'id': program_video.id,
            "description": 'About video',
            "is_approved": True,
            "title": 'Video v2',
            'editor': editor_user.username
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

    assert data == [
        {
            'id': lesson_photoshop_retouch.id,
            "is_approved": True,
            "title": "About Photoshop retouch v2",
            "theory": 'You can retouch in photoshop',
            'practice': 'What you can do in photoshop?',
            'answer': 'retouch',
            "parent_id": None,
            "editor_id": editor_user.pk,
            'theme_id': None,
            'program_id': program_photo.pk,
            'version_id': lesson_photoshop_retouch.actual_version['id'],
            'editor': editor_user.username
        },
        {
            'id': lesson_lightroom.id,
            "is_approved": True,
            "title": "About Lightroom v2",
            "theory": 'The best app for photo processing',
            'practice': 'The best app for photo processing?',
            'answer': 'lightroom',
            "parent_id": lesson_photoshop_retouch.pk,
            "editor_id": editor_user.pk,
            'theme_id': None,
            'program_id': program_photo.pk,
            'version_id': lesson_lightroom.actual_version['id'],
            'editor': editor_user.username
        },
    ]


def test_add_theme(api_client, editor_user, program_photo):
    api_client.force_login(editor_user)

    resp = api_client.post(f'/api/v1/theme/{program_photo.pk}/', {
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


def test_update_theme(api_client, editor_user, program_photo, theme_photoshop):
    api_client.force_login(editor_user)

    resp = api_client.patch(
        f'/api/v1/theme/{program_photo.pk}/{theme_photoshop.pk}/', dict(
            title="Photoshop v2", description="About photoshop v2"
        )
    )

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert data == {
        'id': theme_photoshop.id,
        "title": "Photoshop v2",
        "description": 'About photoshop v2'
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


def test_update_lesson(api_client, editor_user, program_photo, theme_photoshop, lesson_pixelmator):
    api_client.force_login(editor_user)

    resp = api_client.patch(
        f'/api/v1/lesson/{program_photo.pk}/{lesson_pixelmator.pk}/', dict(
            title="Pixelmator v2", theory="Pixelmator v2", practice="Pixelmator v2"
        )
    )

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert data == {
        'id': theme_photoshop.id,
        "title": "Pixelmator v2",
        "theory": 'Pixelmator v2',
        'practice': 'Pixelmator v2',
        'answer': 'pixelmator',
        "parent": None,
        "editor": editor_user.pk,
        'theme': theme_photoshop.pk,
        'program': program_photo.pk,
    }


def test_program_approve(api_client, editor_user, manager_user, program_photo):
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
            version_id=2, approved=True
        )
    )

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert data == {
        "id": program_photo.id,
        "is_approved": True,
        "title": 'Photo v1 v2',
        "description": 'About photo'
    }

    resp = api_client.get(f'/api/v1/program-approve/{program_photo.pk}/')

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert data == {
        "published": {
            "id": program_photo.id,
            "is_approved": True,
            "title": "Photo v1 v2",
            "description": "About photo",
            "editor": manager_user.first_name,
            "version_id": program_photo.actual_version['id']+2
        },
        "not_approved": []
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

    assert data == {
        "published": {
            'id': program_photo.id,
            "editor": 'Editor',
            "description": "About photo",
            "is_approved": True,
            "title": "Photo v1",
            "version_id": program_photo.actual_version['id']
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

    assert data == {
        "not_approved": [
            {
                'id': program_not_approve.id,
                "editor": 'Editor',
                "description": "description",
                "is_approved": False,
                "title": "Not v1",
                "version_id": 1
            }
        ]
    }


def test_theme_approve(api_client, editor_user, manager_user, program_photo, theme_photoshop):
    theme_photoshop.title = theme_photoshop.title + ' v1'
    with reversion.create_revision():
        reversion.set_user(editor_user)
        theme_photoshop.save()

    theme_photoshop.title = theme_photoshop.title + ' v2'
    with reversion.create_revision():
        reversion.set_user(editor_user)
        theme_photoshop.save()

    api_client.force_login(manager_user)

    resp = api_client.put(
        f'/api/v1/theme-approve/{theme_photoshop.id}/', dict(
            version_id=1, approved=True
        )
    )

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert data == {
        'id': theme_photoshop.id,
        "is_approved": True,
        "title": "Photoshop v1",
        "description": "About photoshop",
        "program": program_photo.id
    }


def test_theme_approve_get(api_client, program_photo, manager_user, editor_user, theme_photoshop):
    theme_photoshop.title = theme_photoshop.title + ' v1'
    theme_photoshop.is_approved = True
    with reversion.create_revision():
        reversion.set_user(editor_user)
        theme_photoshop.save()

    api_client.force_login(manager_user)

    resp = api_client.get(f'/api/v1/theme-approve/{theme_photoshop.pk}/')

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert data == {
        "published": {
            'id': theme_photoshop.id,
            "is_approved": True,
            "program_id": program_photo.id,
            "title": "Photoshop v1",
            "description": "About photoshop",
            "version_id": theme_photoshop.actual_version['id'],
            'editor': editor_user.username
        },
        "not_approved": []
    }


def test_theme_not_approve_get(api_client, program_photo, manager_user, editor_user, theme_not_approve):
    theme_not_approve.title = theme_not_approve.title + ' v1'
    with reversion.create_revision():
        reversion.set_user(editor_user)
        theme_not_approve.save()

    api_client.force_login(manager_user)

    resp = api_client.get(f'/api/v1/theme-approve/{theme_not_approve.pk}/')

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data
    
    assert data == {
        "not_approved": [
            {
                'id': theme_not_approve.id,
                "is_approved": False,
                "program_id": program_photo.id,
                "title": "Theme not v1",
                "description": "not theme",
                "version_id": 1,
                'editor': editor_user.username
            }
        ]
    }


def test_lesson_approve(api_client, editor_user, manager_user, program_photo, lesson_lightroom):
    lesson_lightroom.title = lesson_lightroom.title + ' v1'
    with reversion.create_revision():
        reversion.set_user(editor_user)
        lesson_lightroom.save()

    lesson_lightroom.title = lesson_lightroom.title + ' v2'
    with reversion.create_revision():
        reversion.set_user(editor_user)
        lesson_lightroom.save()

    api_client.force_login(manager_user)

    resp = api_client.put(
        f'/api/v1/lesson-approve/{lesson_lightroom.id}/', dict(
            version_id=1, approved=True
        )
    )

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert data == {
        'id': lesson_lightroom.id,
        'is_approved': True,
        'title': 'About Lightroom v1',
        'theory': 'The best app for photo processing',
        'practice': 'The best app for photo processing?',
        'answer': 'lightroom',
        'parent': None,
        "editor": editor_user.pk,
        'program': program_photo.pk,
        'theme': None,
    }


def test_lesson_not_approve(api_client, editor_user, manager_user, program_photo, lesson_not_approve):
    lesson_not_approve.title = lesson_not_approve.title + ' v1'
    with reversion.create_revision():
        reversion.set_user(editor_user)
        lesson_not_approve.save()

    api_client.force_login(manager_user)

    resp = api_client.put(
        f'/api/v1/lesson-approve/{lesson_not_approve.id}/', dict(
            version_id=1, approved=False
        ), format="json"
    )

    assert resp.status_code == status.HTTP_200_OK
    assert Version.objects.filter(pk=1).first() is None


def test_theme_not_approve(api_client, editor_user, manager_user, program_photo, theme_not_approve):
    theme_not_approve.title = theme_not_approve.title + ' v1'
    with reversion.create_revision():
        reversion.set_user(editor_user)
        theme_not_approve.save()

    api_client.force_login(manager_user)

    resp = api_client.put(
        f'/api/v1/theme-approve/{theme_not_approve.id}/', dict(
            version_id=1, approved=False
        ), format="json"
    )

    assert resp.status_code == status.HTTP_200_OK
    assert Version.objects.filter(pk=1).first() is None


def test_program_not_approve(api_client, editor_user, manager_user, program_not_approve):
    program_not_approve.title = program_not_approve.title + ' v1'
    with reversion.create_revision():
        reversion.set_user(editor_user)
        program_not_approve.save()

    api_client.force_login(manager_user)

    resp = api_client.put(
        f'/api/v1/program-approve/{program_not_approve.id}/', dict(
            version_id=1, approved=False
        ), format="json"
    )

    assert resp.status_code == status.HTTP_200_OK
    assert Version.objects.filter(pk=1).first() is None


def test_lesson_approve_get(api_client, program_photo, manager_user, editor_user, lesson_lightroom):
    lesson_lightroom.title = lesson_lightroom.title + ' v1'
    lesson_lightroom.is_approved = True
    with reversion.create_revision():
        reversion.set_user(editor_user)
        lesson_lightroom.save()

    api_client.force_login(manager_user)

    resp = api_client.get(f'/api/v1/lesson-approve/{lesson_lightroom.pk}/')

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert data == {
        'published': {
            'id': lesson_lightroom.id,
            'parent_id': None,
            'is_approved': True,
            "editor_id": editor_user.pk,
            'theme_id': None,
            'title': 'About Lightroom v1',
            'program_id': program_photo.pk,
            'theory': 'The best app for photo processing',
            'practice': 'The best app for photo processing?',
            'answer': 'lightroom',
            "version_id": lesson_lightroom.actual_version['id'],
            'editor': editor_user.username
        },
        "not_approved": []
    }


def test_lesson_not_approve_get(
        api_client, program_photo, manager_user, editor_user, lesson_not_approve
):
    lesson_not_approve.title = lesson_not_approve.title + ' v1'
    with reversion.create_revision():
        reversion.set_user(editor_user)
        lesson_not_approve.save()

    api_client.force_login(manager_user)

    resp = api_client.get(f'/api/v1/lesson-approve/{lesson_not_approve.pk}/')

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data
    
    assert data == {
        "not_approved": [
            {
                'id': lesson_not_approve.id,
                'parent_id': None,
                'is_approved': False,
                "editor_id": editor_user.id,
                'theme_id': None,
                'title': 'Lesson not approve v1',
                'program_id': program_photo.id,
                'theory': 'not_approve_lesson',
                'practice': 'not_approve_lesson',
                'answer': 'answer',
                "version_id": 1,
                'editor': editor_user.username
            }
        ]
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

    assert data == {
        'id': program_photo.id,
        "is_approved": True,
        "title": 'Photo v1',
        "description": "About photo"
    }

    resp = api_client.get(f'/api/v1/program-history/{program_photo.pk}/')

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert data == [{
            'id': program_photo.id,
            "is_approved": True,
            "title": 'Photo v1',
            'version_id': program_photo.actual_version['id'] + 2,
            "description": "About photo",
            'editor': manager_user.username
        },
        {
            'id': program_photo.id,
            "is_approved": True,
            "title": 'Photo v1 v2',
            'version_id': program_photo.actual_version['id'] + 1,
            "description": "About photo",
            'editor': editor_user.username
        },
        {
            'id': program_photo.id,
            "is_approved": True,
            "title": 'Photo v1',
            'version_id': program_photo.actual_version['id'],
            "description": "About photo",
            'editor': editor_user.username
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

    assert data == {
        'id': theme_photoshop.id,
        "is_approved": True,
        "title": 'Photoshop v1',
        "description": "About photoshop",
        "program": program_photo.id
    }

    resp = api_client.get(f'/api/v1/theme-history/{theme_photoshop.pk}/')

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert data == [{
            'id': theme_photoshop.id,
            "is_approved": True,
            "title": 'Photoshop v1',
            "description": "About photoshop",
            "program_id": program_photo.id,
            'version_id': theme_photoshop.actual_version['id'] + 2,
            'editor': manager_user.username
        },
        {
            'id': theme_photoshop.id,
            "is_approved": True,
            "title": 'Photoshop v1 v2',
            "description": "About photoshop",
            "program_id": program_photo.id,
            'version_id': theme_photoshop.actual_version['id'] + 1,
            'editor': editor_user.username
        },
        {
            'id': theme_photoshop.id,
            "is_approved": True,
            "title": 'Photoshop v1',
            "description": "About photoshop",
            "program_id": program_photo.id,
            'version_id': theme_photoshop.actual_version['id'],
            'editor': editor_user.username
        }
    ]


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

    assert data == {
        'id': lesson_photoshop_retouch.id,
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

    resp = api_client.get(f'/api/v1/lesson-history/{lesson_photoshop_retouch.pk}/')

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert data == [
        {
            'id': lesson_photoshop_retouch.id,
            "is_approved": True,
            "title": "About Photoshop retouch v1",
            "theory": 'You can retouch in photoshop',
            'practice': 'What you can do in photoshop?',
            'answer': 'retouch',
            "parent_id": None,
            "editor_id": editor_user.id,
            'theme_id': None,
            'program_id': program_photo.id,
            'version_id': lesson_photoshop_retouch.actual_version['id'] + 2,
            'editor': manager_user.username
        },
        {
            'id': lesson_photoshop_retouch.id,
            "is_approved": True,
            "title": "About Photoshop retouch v1 v2",
            "theory": 'You can retouch in photoshop',
            'practice': 'What you can do in photoshop?',
            'answer': 'retouch',
            "parent_id": None,
            "editor_id": editor_user.id,
            'theme_id': None,
            'program_id': program_photo.id,
            'version_id': lesson_photoshop_retouch.actual_version['id'] + 1,
            'editor': editor_user.username
        },
        {
            'id': lesson_photoshop_retouch.id,
            "is_approved": True,
            "title": "About Photoshop retouch v1",
            "theory": 'You can retouch in photoshop',
            'practice': 'What you can do in photoshop?',
            'answer': 'retouch',
            "parent_id": None,
            "editor_id": editor_user.id,
            'theme_id': None,
            'program_id': program_photo.id,
            'version_id': lesson_photoshop_retouch.actual_version['id'],
            'editor': editor_user.username
        }
    ]


def test_studying(
        api_client, student, student_user, studying, lesson_photoshop_retouch,
        editor_user, program_photo, manager_user):
    
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
        "student": student.id
    }, format="json")

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

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
        'id': studying.id,
        "answer": "retouch",
        "passed": True,
        "lesson": lesson_photoshop_retouch.id,
        "student": student.id
    }

    api_client.force_login(manager_user)

    resp = api_client.get('/api/v1/students-lesson-passed/')

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert data == [
        {
            "user": student_user.id,
            "amount_passed_lesson": 1
        }
    ]

    resp = api_client.get(f'/api/v1/student-subscribed/{program_photo.id}/')

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert data == [{
        "id": program_photo.id,
        "user": student_user.id,
    }]
   

def test_lesson_theme_api_view(
        api_client, program_photo, theme_photoshop, manager_user, editor_user,
        lesson_photoshop_retouch, lesson_lightroom, lesson_pixelmator):
    lesson_photoshop_retouch.title = lesson_photoshop_retouch.title + ' v1'
    lesson_photoshop_retouch.is_approved = True
    with reversion.create_revision():
        reversion.set_user(editor_user)
        lesson_photoshop_retouch.save()

    lesson_lightroom.title = lesson_lightroom.title + ' v1'
    lesson_photoshop_retouch.is_approved = True
    with reversion.create_revision():
        reversion.set_user(editor_user)
        lesson_lightroom.save()

    lesson_pixelmator.title = lesson_pixelmator.title + ' v1'
    lesson_photoshop_retouch.is_approved = True
    with reversion.create_revision():
        reversion.set_user(editor_user)
        lesson_pixelmator.save()

    api_client.force_login(manager_user)

    resp = api_client.get(f'/api/v1/lesson-theme/{program_photo.pk}/')

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert data == {
        "with_theme": [
            {
                "id": theme_photoshop.id,
                "program": program_photo.id,
                "title": "Photoshop",
                "lessons": [
                    {
                        "id": lesson_pixelmator.id,
                        "parent_id": lesson_pixelmator.parent_id,
                        "is_approved": True,
                        "editor_id": editor_user.id,
                        "title": "Pixelmator v1",
                        "program_id": program_photo.id,
                        "theme_id": theme_photoshop.id,
                        "theory": "Pixelmator",
                        "practice": "Pixelmator",
                        "answer": "pixelmator",
                        "editor": editor_user.username
                    }
                ]
            },
        ],
        "without_theme": [
            {
                "id": lesson_photoshop_retouch.id,
                "parent_id": None,
                "is_approved": True,
                "editor_id": editor_user.id,
                "title": "About Photoshop retouch v1",
                "program_id": program_photo.id,
                "theme_id": None,
                "theory": "You can retouch in photoshop",
                "practice": "What you can do in photoshop?",
                "answer": "retouch",
                "editor": editor_user.username
            },
            {
                "id": lesson_lightroom.id,
                "parent_id": lesson_lightroom.parent_id,
                "is_approved": True,
                'editor_id': editor_user.id,
                'title': 'About Lightroom v1',
                "program_id": program_photo.id,
                "theme_id": None,
                "theory": "The best app for photo processing",
                "practice": "The best app for photo processing?",
                "answer": "lightroom",
                "editor": editor_user.username
            }
        ]
    }


def test_lesson_editor_view(
        api_client, program_photo, manager_user, editor_user, theme_photoshop,
        lesson_lightroom, lesson_pixelmator, lesson_photoshop_retouch
):
    lesson_photoshop_retouch.title = lesson_photoshop_retouch.title + ' v1'
    lesson_photoshop_retouch.is_approved = True
    with reversion.create_revision():
        reversion.set_user(editor_user)
        lesson_photoshop_retouch.save()

    lesson_lightroom.title = lesson_lightroom.title + ' v1'
    lesson_photoshop_retouch.is_approved = True
    with reversion.create_revision():
        reversion.set_user(editor_user)
        lesson_lightroom.save()

    lesson_pixelmator.title = lesson_pixelmator.title + ' v1'
    lesson_photoshop_retouch.is_approved = True
    with reversion.create_revision():
        reversion.set_user(editor_user)
        lesson_pixelmator.save()

    api_client.force_login(manager_user)

    resp = api_client.get(f'/api/v1/lesson-editor/{program_photo.pk}/{editor_user.pk}/')

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data

    assert data == [
        {
            "id": lesson_lightroom.id,
            "parent_id": lesson_lightroom.parent_id,
            "is_approved": True,
            'editor_id': editor_user.id,
            'title': 'About Lightroom v1',
            "program_id": program_photo.id,
            "theme_id": None,
            "theory": "The best app for photo processing",
            "practice": "The best app for photo processing?",
            "answer": "lightroom",
            "editor": editor_user.username
        },
        {
            "id": lesson_pixelmator.id,
            "parent_id": lesson_pixelmator.parent_id,
            "is_approved": True,
            "editor_id": editor_user.id,
            "title": "Pixelmator v1",
            "program_id": program_photo.id,
            "theme_id": theme_photoshop.id,
            "theory": "Pixelmator",
            "practice": "Pixelmator",
            "answer": "pixelmator",
            "editor": editor_user.username
        },
        {
            "id": lesson_photoshop_retouch.id,
            "parent_id": lesson_photoshop_retouch.parent_id,
            "is_approved": True,
            "editor_id": editor_user.id,
            "title": "About Photoshop retouch v1",
            "program_id": program_photo.id,
            "theme_id": None,
            "theory": "You can retouch in photoshop",
            "practice": "What you can do in photoshop?",
            "answer": "retouch",
            "editor": editor_user.username
        }
    ]


def test_available_lessons(
    api_client, editor_user, student_user, student, studying,
    program_photo, lesson_photoshop_retouch
):
    lesson_photoshop_retouch.title = lesson_photoshop_retouch.title + ' v2'
    lesson_photoshop_retouch.is_approved = True
    with reversion.create_revision():
        reversion.set_user(editor_user)
        lesson_photoshop_retouch.save()
    
    api_client.force_login(student_user)

    resp = api_client.get(f'/api/v1/available-lessons/{program_photo.pk}/')

    assert resp.status_code == status.HTTP_200_OK
    data = resp.data
    print(data)
    assert data == [
        {
            "id": studying.id,
            "actual_lesson": {
                "id": lesson_photoshop_retouch.id,
                "parent_id": None,
                "is_approved": True,
                "editor_id": editor_user.id,
                "title": 'About Photoshop retouch v2',
                "program_id": program_photo.id,
                "theme_id": None,
                "theory": 'You can retouch in photoshop',
                "practice": 'What you can do in photoshop?',
                "answer": 'retouch',
                "editor": editor_user.username
            },
            "answer": studying.answer,
            "passed": False,
            "lesson": lesson_photoshop_retouch.id,
            "student": student.id
        }
    ]


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


def test_students_lesson_passed_student_login_permission(api_client, student_user):
    api_client.force_login(student_user)

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
