from pathlib import Path

from test_assignments import auth, client


def test_import_roster_authorization_and_idempotency(client):
    csv_text = (Path(__file__).parent.parent / 'docs/examples/mock-students.csv').read_text(encoding='utf-8')
    url = '/courses/1/students/import'
    assert client.post(url, headers=auth(client, 2), json={'csv_text': csv_text}).status_code == 403
    teacher = auth(client, 1)
    response = client.post(url, headers=teacher, json={'csv_text': csv_text})
    assert response.status_code == 200, response.text
    assert response.json() == {'created': 150, 'enrolled': 150}
    assert client.post(url, headers=teacher, json={'csv_text': csv_text}).json() == {'created': 0, 'enrolled': 0}
    users = client.get('/demo/users').json()
    assert len([user for user in users if user.get('student_number')]) == 150


def test_invalid_roster_and_conflicts_are_atomic(client):
    teacher = auth(client, 1)
    url = '/courses/1/students/import'
    header = 'student_number,name,email\n'
    assert client.post(url, headers=teacher, json={'csv_text': header + '220000001,A,a@example.invalid\ninvalid,B,b@example.invalid\n'}).status_code == 422
    assert all(user.get('student_number') != '220000001' for user in client.get('/demo/users').json())
    first = header + '220000001,A,a@example.invalid\n'
    assert client.post(url, headers=teacher, json={'csv_text': first}).status_code == 200
    conflict = header + '220000002,B,b@example.invalid\n220000001,A,other@example.invalid\n'
    assert client.post(url, headers=teacher, json={'csv_text': conflict}).status_code == 409
    assert all(user.get('student_number') != '220000002' for user in client.get('/demo/users').json())


def test_roster_rejects_duplicate_numbers_and_wrong_columns(client):
    teacher = auth(client, 1)
    url = '/courses/1/students/import'
    assert client.post(url, headers=teacher, json={'csv_text': 'name,email\nA,a@example.invalid\n'}).status_code == 422
    text = 'student_number,name,email\n220000001,A,a@example.invalid\n220000001,B,b@example.invalid\n'
    assert client.post(url, headers=teacher, json={'csv_text': text}).status_code == 422
