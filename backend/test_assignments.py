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


def test_checker_visibility_and_rule_snapshot(client):
    teacher, student, other = auth(client, 1), auth(client, 2), auth(client, 4)
    rule = {'id': str(uuid4()), 'tag': 'h1', 'attrs': {}, 'min_count': 1, 'non_empty': True, 'inside': None, 'label_linked': False}
    assignment = {'course_id': 1, 'title': 'Form', 'enabled_languages': ['html'], 'checker_enabled': True, 'check_rules': [rule]}
    assignment_id = client.post('/assignments', headers=teacher, json=assignment).json()['id']
    url = f'/assignments/{assignment_id}'
    assert client.get(url, headers=teacher).json()['check_rules'][0]['id'] == rule['id']
    assert 'check_rules' not in client.get(url, headers=student).json()
    assert 'check_rules' not in client.get('/courses/1/assignments', headers=student).json()[0]
    client.post('/me/recording-consent', headers=student)
    client.post(f'{url}/draft', headers=student)
    code = {'html': '<h1>Merhaba</h1>', 'css': '', 'javascript': ''}
    batch = {'batch_id': str(uuid4()), 'code': code, 'events': [{'t_ms': 1, 'kind': 'edit', 'payload': {'language': 'html', 'changes': [{'rangeOffset': 0, 'rangeLength': 0, 'text': code['html']}]}}]}
    assert client.post(f'{url}/draft/batches', headers=student, json=batch).status_code == 200
    submission = client.post(f'{url}/submit', headers=student, json=code)
    assert submission.status_code == 200
    detail_url = f"/submissions/{submission.json()['id']}"
    assert 'check_result' not in client.get(detail_url, headers=student).json()
    assert client.get(detail_url, headers=other).status_code == 403
    result = client.get(detail_url, headers=teacher).json()['check_result']
    assert result[0]['used'] and result[0]['count'] == 1 and result[0]['rule'] == rule
    assignment['show_results_to_student'] = True
    assignment['check_rules'] = []
    assert client.put(url, headers=teacher, json=assignment).status_code == 200
    assert client.get(detail_url, headers=student).json()['check_result'][0]['rule'] == rule
    assignment['checker_enabled'] = False
    assert client.put(url, headers=teacher, json=assignment).status_code == 200
    assert 'check_result' not in client.get(detail_url, headers=teacher).json()
    assert 'check_result' not in client.get(detail_url, headers=student).json()


def test_checker_off_does_not_produce_result(client, monkeypatch):
    def unexpected_checker(*_args):
        raise AssertionError('Checker must not run when disabled')

    monkeypatch.setattr('submissions.run_checker', unexpected_checker)
    teacher, student = auth(client, 1), auth(client, 2)
    assignment = {'course_id': 1, 'title': 'Kapalı', 'enabled_languages': ['html'], 'checker_enabled': False, 'show_results_to_student': True}
    assignment_id = client.post('/assignments', headers=teacher, json=assignment).json()['id']
    client.post('/me/recording-consent', headers=student)
    client.post(f'/assignments/{assignment_id}/draft', headers=student)
    submission = client.post(f'/assignments/{assignment_id}/submit', headers=student, json={'html': '', 'css': '', 'javascript': ''})
    assert submission.status_code == 200
    assert 'check_result' not in client.get(f"/submissions/{submission.json()['id']}", headers=teacher).json()


def test_writing_report_is_teacher_only_and_diagnostics_are_independent(client):
    teacher, student, other = auth(client, 1), auth(client, 2), auth(client, 4)
    assignment = {'course_id': 1, 'title': 'Yazım', 'enabled_languages': ['html'],
                  'starter_code': {'html': '<img>', 'css': '', 'javascript': ''},
                  'diagnostics_enabled': True, 'intellisense_enabled': False,
                  'lint_rules': ['html_alt'], 'show_results_to_student': True}
    created = client.post('/assignments', headers=teacher, json=assignment)
    assert created.status_code == 201
    assignment_id = created.json()['id']
    student_assignment = client.get(f'/assignments/{assignment_id}', headers=student).json()
    assert student_assignment['diagnostics_enabled'] is True
    assert student_assignment['intellisense_enabled'] is False
    assert 'lint_rules' not in student_assignment
    client.post('/me/recording-consent', headers=student)
    client.post(f'/assignments/{assignment_id}/draft', headers=student)
    result = client.post(f'/assignments/{assignment_id}/submit', headers=student, json=assignment['starter_code'])
    assert result.status_code == 200
    url = f"/submissions/{result.json()['id']}"
    report = client.get(url, headers=teacher).json()['lint_report']
    assert [item['rule'] for item in report] == ['alt-require']
    assert report[0]['message'] == 'Görsel için alt açıklaması ekleyin.'
    assert 'lint_report' not in client.get(url, headers=student).json()
    assert client.get(url, headers=other).status_code == 403


def test_writing_check_failure_does_not_submit(client, monkeypatch):
    teacher, student = auth(client, 1), auth(client, 2)
    assignment = {'course_id': 1, 'title': 'Yazım', 'enabled_languages': ['html'], 'lint_rules': ['html_alt']}
    assignment_id = client.post('/assignments', headers=teacher, json=assignment).json()['id']
    client.post('/me/recording-consent', headers=student)
    client.post(f'/assignments/{assignment_id}/draft', headers=student)
    def fail(*_args):
        raise RuntimeError('timeout')
    monkeypatch.setattr('submissions.run_writing_checks', fail)
    response = client.post(f'/assignments/{assignment_id}/submit', headers=student, json={'html': '', 'css': '', 'javascript': ''})
    assert response.status_code == 503
    assert client.get(f'/assignments/{assignment_id}/submissions', headers=teacher).json() == []


def test_assignment_criteria_are_validated_saved_and_private(client):
    teacher, student, outsider = auth(client, 1), auth(client, 2), auth(client, 3)
    rule_id, auto_id, manual_id = str(uuid4()), str(uuid4()), str(uuid4())
    payload = {
        'course_id': 1, 'title': 'Rubrik', 'enabled_languages': ['html'], 'checker_enabled': True,
        'check_rules': [{'id': rule_id, 'tag': 'h1'}],
        'criteria': [
            {'id': auto_id, 'kind': 'auto', 'label': 'Başlık kullanımı', 'max_points': '12.50', 'check_rule_ref': rule_id},
            {'id': manual_id, 'kind': 'manual', 'label': 'Sunum', 'max_points': '7.25', 'check_rule_ref': None},
        ],
    }
    response = client.post('/assignments', headers=student, json=payload)
    assert response.status_code == 403
    response = client.post('/assignments', headers=teacher, json=payload)
    assert response.status_code == 201, response.text
    assignment_id = response.json()['id']
    assert [(item['kind'], item['max_points']) for item in response.json()['criteria']] == [('auto', '12.50'), ('manual', '7.25')]
    url = f'/assignments/{assignment_id}'
    assert 'criteria' not in client.get(url, headers=student).json()
    assert client.get(url, headers=outsider).status_code == 403
    assert 'criteria' not in client.get('/courses/1/assignments', headers=student).json()[0]
    payload['criteria'][1]['max_points'] = '8.00'
    assert client.put(url, headers=teacher, json=payload).json()['criteria'][1]['max_points'] == '8.00'
    without_criteria = {key: value for key, value in payload.items() if key != 'criteria'}
    assert len(client.put(url, headers=teacher, json=without_criteria).json()['criteria']) == 2
    without_criteria['checker_enabled'] = False
    assert len(client.put(url, headers=teacher, json=without_criteria).json()['criteria']) == 2
    payload['check_rules'] = []
    assert client.put(url, headers=teacher, json=payload).status_code == 422
    payload['check_rules'] = [{'id': rule_id, 'tag': 'h1'}]
    payload['criteria'][0]['max_points'] = '-1'
    assert client.put(url, headers=teacher, json=payload).status_code == 422
    payload['criteria'] = [payload['criteria'][1]]
    payload['check_rules'] = []
    payload['checker_enabled'] = False
    response = client.put(url, headers=teacher, json=payload)
    assert response.status_code == 200
    assert [item['id'] for item in response.json()['criteria']] == [manual_id]
