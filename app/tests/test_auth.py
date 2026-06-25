"""
Tests for /auth endpoints:
  POST /auth/register
  POST /auth/login
  GET  /auth/me
"""
import pytest
from app.tests.conftest import register_user, login_user, auth_headers


# ── Registration ─────────────────────────────────────────────────────────────

class TestRegister:

    def test_register_success(self, client, clean_db):
        resp = register_user(client)
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["role"] == "student"
        assert "id" in data
        # hashed_password must NEVER be returned
        assert "hashed_password" not in data
        assert "password" not in data

    def test_register_duplicate_username(self, client, clean_db):
        register_user(client)
        resp = register_user(client)  # same username
        assert resp.status_code == 400
        assert resp.json()["detail"] == "Username already exists"

    def test_register_duplicate_email(self, client, clean_db):
        register_user(client, username="user1", email="same@example.com")
        resp = register_user(client, username="user2", email="same@example.com")
        assert resp.status_code == 400
        assert resp.json()["detail"] == "Email already exists"

    def test_register_invalid_email(self, client, clean_db):
        resp = client.post("/auth/register", json={
            "username": "testuser",
            "email": "not-an-email",
            "password": "secret123",
            "role": "student",
        })
        assert resp.status_code == 422

    def test_register_short_password(self, client, clean_db):
        resp = client.post("/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "abc",   # < 6 chars
            "role": "student",
        })
        assert resp.status_code == 422

    def test_register_missing_fields(self, client, clean_db):
        resp = client.post("/auth/register", json={"username": "testuser"})
        assert resp.status_code == 422


# ── Login ─────────────────────────────────────────────────────────────────────

class TestLogin:

    def test_login_success(self, client, clean_db):
        register_user(client)
        resp = login_user(client)
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, clean_db):
        register_user(client)
        resp = login_user(client, password="wrongpassword")
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid username or password"

    def test_login_nonexistent_user(self, client, clean_db):
        resp = login_user(client, username="ghost")
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid username or password"

    def test_login_requires_form_data(self, client, clean_db):
        """Login endpoint must reject JSON bodies (OAuth2 form requirement)."""
        register_user(client)
        resp = client.post("/auth/login", json={
            "username": "testuser",
            "password": "secret123",
        })
        assert resp.status_code == 422  # form data expected, not JSON


# ── /me ───────────────────────────────────────────────────────────────────────

class TestMe:

    def test_me_returns_current_user(self, client, clean_db):
        register_user(client)
        headers = auth_headers(client)
        resp = client.get("/auth/me", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    def test_me_without_token(self, client):
        resp = client.get("/auth/me")
        assert resp.status_code == 401

    def test_me_with_invalid_token(self, client):
        resp = client.get("/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
        assert resp.status_code == 401
