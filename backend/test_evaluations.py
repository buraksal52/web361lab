import csv
import io
from uuid import uuid4

from test_assignments import auth, client


def create_submission(client, show_criteria=False, checker_enabled=True):
    teacher, student = auth(client, 1), auth(client, 2)
    rule_id, auto_id, manual_id = str(uuid4()), str(uuid4()), str(uuid4())
    code = {'html': '<h1>Başlık</h1>', 'css': '', 'javascript': ''}
    assignment = {'course_id': 1, 'title': 'Rubrik', 'enabled_languages': ['html'], 'starter_code': code,
                  'checker_enabled': checker_enabled, 'show_criteria_to_student': show_criteria,
                  'check_rules': [{'id': rule_id, 'tag': 'h1'}],
                  'criteria': [{'id': auto_id, 'kind': 'auto', 'label': 'Başlık', 'max_points': '10.50', 'check_rule_ref': rule_id},
                               {'id': manual_id, 'kind': 'manual', 'label': 'Sunum', 'max_points': '4.75'}]}
    response = client.post('/assignments', headers=teacher, json=assignment)
    assert response.status_code == 201, response.text
    assignment_id = response.json()['id']
    client.post('/me/recording-consent', headers=student)
    client.post(f'/assignments/{assignment_id}/draft', headers=student)
    response = client.post(f'/assignments/{assignment_id}/submit', headers=student, json=code)
    assert response.status_code == 200, response.text
    return teacher, student, assignment_id, response.json()['id'], assignment, auto_id, manual_id


def score_payload(view, auto_id, manual_id, override=None, manual='2.25'):
    return {'submitted_at': view['submitted_at'], 'rubric_fingerprint': view['rubric_fingerprint'],
            'final_points': '11.75', 'feedback': '=Örnek',
            'criteria': [{'criterion_id': auto_id, 'teacher_override': override},
                         {'criterion_id': manual_id, 'manual_points': manual}]}


def test_grade_suggestion_overrides_feedback_and_csv(client):
    teacher, student, assignment_id, submission_id, _, auto_id, manual_id = create_submission(client)
    other = auth(client, 4)
    url = f'/submissions/{submission_id}/evaluation'
    assert client.get(url, headers=student).status_code == 403
    assert client.get(url, headers=other).status_code == 403
    view = client.get(url, headers=teacher).json()
    assert view['criteria'][0]['auto_result'] is True
    assert view['suggested_points'] is None
    payload = score_payload(view, auto_id, manual_id)
    assert client.put(url, headers=student, json=payload).status_code == 403
    response = client.put(url, headers=teacher, json=payload)
    assert response.status_code == 200, response.text
    assert response.json()['suggested_points'] == '12.75'
    assert response.json()['final_points'] == '11.75'
    saved = client.get(url, headers=teacher).json()
    assert saved['suggested_points'] == '12.75'
    assert saved['criteria'][0]['points'] == '10.50'
    assert client.get(f'/submissions/{submission_id}/feedback', headers=student).json() == {'final_points': '11.75', 'feedback': '=Örnek'}
    assert client.get(f'/submissions/{submission_id}/feedback', headers=other).status_code == 403
    assert client.get(f'/assignments/{assignment_id}/grades.csv', headers=student).status_code == 403
    response = client.get(f'/assignments/{assignment_id}/grades.csv', headers=teacher)
    rows = list(csv.reader(io.StringIO(response.content.decode('utf-8-sig'))))
    assert rows[1] == ['Student', 'student@example.invalid', '11.75', "'=Örnek"]
    payload['criteria'][0]['teacher_override'] = False
    assert client.put(url, headers=teacher, json=payload).json()['suggested_points'] == '2.25'
    saved = client.get(url, headers=teacher).json()
    assert saved['criteria'][0]['auto_result'] is True and saved['criteria'][0]['teacher_override'] is False


def test_grade_rejects_partial_auto_and_out_of_range_manual(client):
    teacher, _, _, submission_id, _, auto_id, manual_id = create_submission(client)
    url = f'/submissions/{submission_id}/evaluation'
    view = client.get(url, headers=teacher).json()
    payload = score_payload(view, auto_id, manual_id)
    payload['criteria'][0]['manual_points'] = '3.00'
    assert client.put(url, headers=teacher, json=payload).status_code == 422
    payload = score_payload(view, auto_id, manual_id, manual='4.76')
    assert client.put(url, headers=teacher, json=payload).status_code == 422
    payload = score_payload(view, auto_id, manual_id)
    payload['criteria'].pop()
    assert client.put(url, headers=teacher, json=payload).status_code == 422


def test_no_checker_result_requires_instructor_choice(client):
    teacher, _, _, submission_id, _, auto_id, manual_id = create_submission(client, checker_enabled=False)
    url = f'/submissions/{submission_id}/evaluation'
    view = client.get(url, headers=teacher).json()
    assert view['criteria'][0]['auto_result'] is None
    payload = score_payload(view, auto_id, manual_id)
    assert client.put(url, headers=teacher, json=payload).status_code == 422
    payload['criteria'][0]['teacher_override'] = True
    assert client.put(url, headers=teacher, json=payload).json()['suggested_points'] == '12.75'


def test_resubmission_keeps_old_grade_but_does_not_export_it(client):
    teacher, student, assignment_id, submission_id, _, auto_id, manual_id = create_submission(client)
    url = f'/submissions/{submission_id}/evaluation'
    view = client.get(url, headers=teacher).json()
    payload = score_payload(view, auto_id, manual_id)
    assert client.put(url, headers=teacher, json=payload).status_code == 200
    assert client.post(f'/submissions/{submission_id}/unlock', headers=teacher).status_code == 200
    assert client.put(url, headers=teacher, json=payload).status_code == 409
    resubmit = client.post(f'/assignments/{assignment_id}/submit', headers=student, json={'html': '<h1>Başlık</h1>', 'css': '', 'javascript': ''})
    assert resubmit.status_code == 200
    stale = client.get(url, headers=teacher).json()
    assert stale['previous_evaluation']['final_points'] == '11.75'
    assert stale['final_points'] is None
    assert client.get(f'/submissions/{submission_id}/feedback', headers=student).json()['final_points'] is None
    assert len(list(csv.reader(io.StringIO(client.get(f'/assignments/{assignment_id}/grades.csv', headers=teacher).content.decode('utf-8-sig'))))) == 1
    assert client.put(url, headers=teacher, json=payload).status_code == 409


def test_criteria_visibility_is_independent_of_check_result_visibility(client):
    teacher, student, assignment_id, _, assignment, _, _ = create_submission(client)
    url = f'/assignments/{assignment_id}'
    assert 'criteria' not in client.get(url, headers=student).json()
    assignment['show_criteria_to_student'] = True
    assert client.put(url, headers=teacher, json=assignment).status_code == 200
    visible = client.get(url, headers=student).json()
    assert len(visible['criteria']) == 2
    assert 'check_rules' not in visible
