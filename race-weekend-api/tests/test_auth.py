# tests/test_auth.py
from tests.conftest import register_user

def test_register_and_login(client):
    r = register_user(client)
    assert r.status_code == 201
    assert r.json()["email"] == "user@test.com"

    login = client.post("/v1/auth/login", json={"email": "user@test.com", "password": "StrongPass1!"})
    assert login.status_code == 200
    assert "access_token" in login.json()

def test_register_rejects_weak_password(client):
    r = client.post("/v1/auth/register", json={"email": "weak@test.com", "password": "short"})
    assert r.status_code == 422  # pydantic validation error
