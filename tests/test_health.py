import pytest

from app import create_app


@pytest.fixture
def app():
    _app = create_app("development")
    _app.config["TESTING"] = True
    _app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    return _app


@pytest.fixture
def client(app):
    return app.test_client()


def test_health_check_returns_response(client):
    response = client.get("/health")
    assert response.status_code in (200, 503)
    data = response.get_json()
    assert data["service"] == "ProspectAI"
    assert "status" in data
    assert "database" in data


def test_health_check_shape(client):
    response = client.get("/health")
    data = response.get_json()
    assert isinstance(data["success"], bool)
    assert data["service"] == "ProspectAI"
