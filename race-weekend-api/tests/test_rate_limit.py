# tests/test_rate_limit.py
import time

from app.core.config import settings

class FakeRedis:
    def __init__(self):
        self.store = {}

    def incr(self, key):
        self.store[key] = int(self.store.get(key, 0)) + 1
        return self.store[key]

    def expire(self, key, _seconds):
        return True

    def get(self, key):
        return None

    def setex(self, key, ttl, value):
        return True

def test_rate_limit_headers_present(client, app):
    # register/login
    client.post("/v1/auth/register", json={"email": "u@x.com", "password": "StrongPass1!"})
    token = client.post("/v1/auth/login", json={"email": "u@x.com", "password": "StrongPass1!"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # override Redis dependency
    from app.api.v1 import routes_tasks
    app.dependency_overrides[routes_tasks.get_redis] = lambda: FakeRedis()

    resp = client.get("/v1/tasks", headers=headers)
    assert resp.status_code == 200
    assert "X-RateLimit-Limit" in resp.headers
    assert "X-RateLimit-Remaining" in resp.headers
    assert "X-RateLimit-Reset" in resp.headers
