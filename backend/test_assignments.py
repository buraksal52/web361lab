import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app
from models import Course, Enrollment, User


@pytest.fixture
def client():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine)
    with sessions() as db:
        db.add_all([User(id=1, name='Teacher', email='teacher@example.invalid', role='teacher'), User(id=2, name='Student', email='student@example.invalid', role='student'), User(id=3, name='Outside', email='outside@example.invalid', role='student'), User(id=4, name='Other', email='other@example.invalid', role='student'), Course(id=1, name='Course')])
        db.add_all([Enrollment(user_id=1, course_id=1, role='teacher'), Enrollment(user_id=2, course_id=1, role='student'), Enrollment(user_id=4, course_id=1, role='student')])
        db.commit()

    def override_db():
        with sessions() as db:
            yield db

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()


def auth(client, user_id):
    token = client.post(f'/demo/login/{user_id}').json()['token']
    return {'Authorization': f'Bearer {token}'}


def test_assignment_access_and_editing(client):
    teacher = auth(client, 1)
    student = auth(client, 2)
    outsider = auth(client, 3)
    payload = {'course_id': 1, 'title': 'Form', 'enabled_languages': ['html'], 'paste_enabled': False}
    assert client.post('/assignments', json=payload, headers=student).status_code == 403
    created = client.post('/assignments', json=payload, headers=teacher)
    assert created.status_code == 201
    assignment_id = created.json()['id']
    assert client.get(f'/assignments/{assignment_id}', headers=student).json()['enabled_languages'] == ['html']
    assert client.get(f'/assignments/{assignment_id}', headers=outsider).status_code == 403
    assert client.get('/courses/1/assignments', headers=outsider).status_code == 403
    assert client.get(f'/assignments/{assignment_id}').status_code == 401
    payload['title'] = 'Updated'
    assert client.put(f'/assignments/{assignment_id}', json=payload, headers=student).status_code == 403
    assert client.put(f'/assignments/{assignment_id}', json=payload, headers=teacher).json()['title'] == 'Updated'
    assert client.post('/demo/logout', headers=teacher).status_code == 200
    assert client.get('/courses', headers=teacher).status_code == 401


def test_draft_recording_requires_consent_and_is_private(client):
    teacher, student, outsider = auth(client, 1), auth(client, 2), auth(client, 3)
    payload = {'course_id': 1, 'title': 'Form', 'enabled_languages': ['html'], 'starter_code': {'html': '😀', 'css': '', 'javascript': ''}}
    assignment_id = client.post('/assignments', json=payload, headers=teacher).json()['id']
    draft_url = f'/assignments/{assignment_id}/draft'
    assert client.post(draft_url, headers=student).status_code == 403
    before_consent = {'batch_id': str(uuid4()), 'code': {'html': '😀', 'css': '', 'javascript': ''}, 'events': [{'t_ms': 0, 'kind': 'blur', 'payload': {}}]}
    assert client.post(f'{draft_url}/batches', json=before_consent, headers=student).status_code == 403
    assert client.get(f'/assignments/{assignment_id}/students/2/replay', headers=teacher).status_code == 404
    assert client.post('/me/recording-consent', headers=student).status_code == 200
    assert client.post(draft_url, headers=outsider).status_code == 403
    assert client.post(draft_url, headers=teacher).status_code == 403
    assert client.post(draft_url, headers=student).json()['code']['html'] == '😀'

    batch = {'batch_id': str(uuid4()), 'code': {'html': '😀ok', 'css': '', 'javascript': ''}, 'events': [
        {'t_ms': 10, 'kind': 'edit', 'payload': {'language': 'html', 'changes': [{'rangeOffset': 2, 'rangeLength': 0, 'text': 'ok'}]}},
        {'t_ms': 11, 'kind': 'paste_blocked', 'payload': {}},
        {'t_ms': 12, 'kind': 'blur', 'payload': {}},
    ]}
    saved = client.post(f'{draft_url}/batches', json=batch, headers=student)
    assert saved.status_code == 200
    assert saved.json()['signals'] == {'paste_blocked_count': 1, 'blur_count': 1, 'max_insert_chars': 2}
    assert client.post(f'{draft_url}/batches', json=batch, headers=student).json()['signals'] == saved.json()['signals']
    assert client.post(draft_url, headers=student).json()['code']['html'] == '😀ok'
    replay_url = f'/assignments/{assignment_id}/students/2/replay'
    assert client.get(replay_url, headers=outsider).status_code == 403
    replay = client.get(replay_url, headers=teacher).json()
    assert replay['initial_code']['html'] == '😀'
    assert len(replay['events']) == 3
    change = replay['events'][0]['payload']['changes'][0]
    original = replay['initial_code']['html'].encode('utf-16-le')
    start = change['rangeOffset'] * 2
    end = start + change['rangeLength'] * 2
    assert (original[:start] + change['text'].encode('utf-16-le') + original[end:]).decode('utf-16-le') == replay['code']['html']

    invalid = {'batch_id': str(uuid4()), 'code': {'html': 'changed', 'css': '', 'javascript': ''}, 'events': []}
    assert client.post(f'{draft_url}/batches', json=invalid, headers=student).status_code == 400
    assert client.get(replay_url, headers=student).json()['code']['html'] == '😀ok'


def test_submit_lock_teacher_review_and_unlock(client):
    teacher, student, outsider = auth(client, 1), auth(client, 2), auth(client, 3)
    other_student = auth(client, 4)
    assignment_id = client.post('/assignments', headers=teacher, json={'course_id': 1, 'title': 'Ödev', 'enabled_languages': ['html']}).json()['id']
    url = f'/assignments/{assignment_id}'
    code = {'html': '<h1>Merhaba</h1>', 'css': '', 'javascript': ''}
    assert client.post(f'{url}/submit', headers=student, json=code).status_code == 403
    client.post('/me/recording-consent', headers=student)
    client.post(f'{url}/draft', headers=student)
    assert client.post(f'{url}/submit', headers=student, json=code).status_code == 409
    batch = {'batch_id': str(uuid4()), 'code': code, 'events': [{'t_ms': 20, 'kind': 'edit', 'payload': {'language': 'html', 'changes': [{'rangeOffset': 0, 'rangeLength': 0, 'text': code['html']}]}}]}
    assert client.post(f'{url}/draft/batches', headers=student, json=batch).status_code == 200
    response = client.post(f'{url}/submit', headers=student, json=code)
    assert response.status_code == 200
    submission_id = response.json()['id']
    assert client.post(f'{url}/submit', headers=student, json=code).status_code == 409
    assert client.post(f'{url}/draft', headers=student).json()['locked'] is True
    later = {'batch_id': str(uuid4()), 'code': code, 'events': [{'t_ms': 30, 'kind': 'blur', 'payload': {}}]}
    assert client.post(f'{url}/draft/batches', headers=student, json=later).status_code == 409
    assert client.get(f'{url}/submissions', headers=student).status_code == 403
    assert client.get(f'/submissions/{submission_id}', headers=outsider).status_code == 403
    assert client.get(f'/submissions/{submission_id}', headers=other_student).status_code == 403
    assert client.get(f'{url}/students/2/replay', headers=other_student).status_code == 403
    assert client.get(f'/submissions/{submission_id}', headers=teacher).json()['final_code'] == code
    assert client.get(f'{url}/submissions', headers=teacher).json()[0]['student_name'] == 'Student'
    assert client.get(f'{url}/students/2/replay', headers=teacher).json()['events'][-1]['kind'] == 'submit'
    assert client.post(f'/submissions/{submission_id}/unlock', headers=student).status_code == 403
    assert client.post(f'/submissions/{submission_id}/unlock', headers=teacher).status_code == 200
    assert client.post(f'{url}/draft/batches', headers=student, json=later).status_code == 200
    assert client.post(f'{url}/submit', headers=student, json=code).status_code == 200
