"""
Shared test fixtures for student-result-mng tests.

Uses an in-memory SQLite database so tests never touch real MySQL.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app

# ── In-memory SQLite for tests ───────────────────────────────────────────────
SQLALCHEMY_TEST_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override DB dependency for all tests
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    """Create all tables once for the test session."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    """HTTP test client — fresh for each test."""
    return TestClient(app)


@pytest.fixture()
def clean_db():
    """Wipe all rows between tests that need isolation."""
    yield
    db = TestingSessionLocal()
    from models import User, Student
    db.query(Student).delete()
    db.query(User).delete()
    db.commit()
    db.close()


# ── Reusable helpers ─────────────────────────────────────────────────────────

def register_user(client, username="testuser", email="test@example.com", password="secret123"):
    return client.post("/auth/register", json={
        "username": username,
        "email": email,
        "password": password,
        "role": "student",
    })


def login_user(client, username="testuser", password="secret123"):
    return client.post("/auth/login", data={
        "username": username,
        "password": password,
    })


def auth_headers(client, username="testuser", password="secret123"):
    resp = login_user(client, username, password)
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
