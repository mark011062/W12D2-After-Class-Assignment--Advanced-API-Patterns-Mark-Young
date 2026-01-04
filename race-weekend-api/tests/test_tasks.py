# tests/test_tasks.py
from sqlalchemy import select

from app.db.models import User
from tests.conftest import register_user, login_user


class FakeRedis:
    """
    Minimal Redis stub for rate limiting.
    Supports the methods your rate_limit code calls: incr(), expire().
    """
    def __init__(self):
        self.store = {}

    def incr(self, key):
        self.store[key] = int(self.store.get(key, 0)) + 1
        return self.store[key]

    def expire(self, key, _seconds):
        return True

    # Optional methods (in case your code touches them)
    def get(self, key):
        return None

    def setex(self, key, ttl, value):
        return True


def make_admin(db_session, email="admin@test.com"):
    user = db_session.execute(select(User).where(User.email == email)).scalar_one()
    user.role = "admin"
    db_session.commit()
    db_session.refresh(user)
    return user


def get_user_id(db_session, email: str) -> int:
    user = db_session.execute(select(User).where(User.email == email)).scalar_one()
    return user.id


def test_tasks_crud_flow(client, app, db_session):
    # IMPORTANT: override Redis dependency so tests don't try to connect to docker host "redis"
    from app.api.v1 import routes_tasks
    app.dependency_overrides[routes_tasks.get_redis] = lambda: FakeRedis()

    # register + login normal user
    register_user(client, email="user@test.com", password="StrongPass1!")
    token = login_user(client, email="user@test.com", password="StrongPass1!")
    headers = {"Authorization": f"Bearer {token}"}

    user_id = get_user_id(db_session, "user@test.com")

    # create event requires admin -> should fail for normal user
    ev = client.post(
        "/v1/events",
        json={
            "name": "NCM Weekend",
            "track_name": "NCM Motorsports Park",
            "city": "Bowling Green",
            "state": "KY",
            "event_date": "2026-01-10",
        },
        headers=headers,
    )
    assert ev.status_code in (401, 403)

    # create admin and create event
    register_user(client, email="admin@test.com", password="StrongAdmin1!")
    make_admin(db_session, email="admin@test.com")

    admin_token = login_user(client, email="admin@test.com", password="StrongAdmin1!")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    ev = client.post(
        "/v1/events",
        json={
            "name": "NCM Weekend",
            "track_name": "NCM Motorsports Park",
            "city": "Bowling Green",
            "state": "KY",
            "event_date": "2026-01-10",
        },
        headers=admin_headers,
    )
    assert ev.status_code == 201
    event_id = ev.json()["id"]

    # create task assigned to user (admin assigning ok)
    t = client.post(
        "/v1/tasks",
        json={
            "event_id": event_id,
            "title": "Safety wire oil drain bolt",
            "description": "Prep for tech inspection",
            "category": "tech",
            "priority": 1,
            "assignee_id": user_id,
        },
        headers=admin_headers,
    )
    assert t.status_code == 201
    task_id = t.json()["id"]

    # user can see assigned task
    g = client.get(f"/v1/tasks/{task_id}", headers=headers)
    assert g.status_code == 200
    assert g.json()["title"] == "Safety wire oil drain bolt"

    # user updates completion
    u = client.patch(f"/v1/tasks/{task_id}", json={"completed": True}, headers=headers)
    assert u.status_code == 200
    assert u.json()["completed"] is True

    # user deletes their assigned task
    d = client.delete(f"/v1/tasks/{task_id}", headers=headers)
    assert d.status_code == 204
