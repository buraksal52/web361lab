import pytest
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
        db.add_all([User(id=1, name='Teacher', email='teacher@example.invalid', role='teacher'), User(id=2, name='Student', email='student@example.invalid', role='student'), User(id=3, name='Outside', email='outside@example.invalid', role='student'), Course(id=1, name='Course')])
        db.add_all([Enrollment(user_id=1, course_id=1, role='teacher'), Enrollment(user_id=2, course_id=1, role='student')])
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
