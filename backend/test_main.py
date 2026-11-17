from fastapi.testclient import TestClient

from main import app


def test_hello():
    response = TestClient(app).get('/hello')
    assert response.status_code == 200
    assert response.json() == {'message': 'Merhaba'}
