# tests/conftest.py
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# -----------------------------------------------------------------------------
# CRITICAL: set a TEST DATABASE_URL at import time (before pytest collection)
# We'll point it at a file DB under pytest's temp folder.
# -----------------------------------------------------------------------------
_TEST_DB_PATH: Path | None = None  # filled in by pytest_sessionstart


def pytest_sessionstart(session):
    """
    This hook runs before tests are collected/executed.
    We set DATABASE_URL here so importing app code never points to Postgres/Docker.
    """
    global _TEST_DB_PATH

    # Use pytest's base temp directory if available; otherwise fall back locally.
    # This will exist by the time hooks run.
    base_temp = Path(session.config._tmp_path_factory.getbasetemp())
    _TEST_DB_PATH = base_temp / "race_weekend_test.db"

    os.environ["ENV"] = "test"
    os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB_PATH}"


@pytest.fixture(scope="session")
def test_db_url() -> str:
    assert _TEST_DB_PATH is not None
    return f"sqlite:///{_TEST_DB_PATH}"


@pytest.fixture(scope="session")
def engine(test_db_url: str):
    """
    Session-wide engine bound to the SQLite file.
    File-based DB avoids in-memory connection isolation issues.
    """
    from app.db.database import Base

    engine = create_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
        future=True,
    )

    Base.metadata.create_all(bind=engine)

    yield engine

    try:
        Base.metadata.drop_all(bind=engine)
    finally:
        engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine):
    """
    New DB session per test function.
    """
    TestingSessionLocal = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, future=True
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def app(db_session):
    """
    Create FastAPI app and override router-level get_db dependencies.
    """
    from app.main import create_app
    from app.api.v1 import routes_auth, routes_events, routes_tasks

    fastapi_app = create_app()

    def override_get_db():
        yield db_session

    fastapi_app.dependency_overrides[routes_auth.get_db] = override_get_db
    fastapi_app.dependency_overrides[routes_events.get_db] = override_get_db
    fastapi_app.dependency_overrides[routes_tasks.get_db] = override_get_db

    return fastapi_app


@pytest.fixture(scope="function")
def client(app):
    with TestClient(app) as c:
        yield c


def register_user(client, email="user@test.com", password="StrongPass1!"):
    return client.post("/v1/auth/register", json={"email": email, "password": password})


def login_user(client, email="user@test.com", password="StrongPass1!"):
    resp = client.post("/v1/auth/login", json={"email": email, "password": password})
    token = resp.json()["access_token"]
    return token
