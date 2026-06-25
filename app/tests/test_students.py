"""
Tests for /student endpoints:
  POST   /student/register
  GET    /student/all-students
  GET    /student/{id}
  PUT    /student/{id}
  DELETE /student/{id}

All routes require a valid JWT — tests register+login a user first.
"""
import pytest
from app.tests.conftest import register_user, auth_headers


# ── Fixture: authenticated headers available for every test in this module ────

@pytest.fixture()
def headers(client, clean_db):
    register_user(client)
    return auth_headers(client)


def create_student(client, headers, roll_no="CS001", name="Alice", email="alice@test.com", semester=3):
    return client.post("/student/register", json={
        "roll_no": roll_no,
        "name": name,
        "email": email,
        "semester": semester,
    }, headers=headers)


# ── Create student ────────────────────────────────────────────────────────────

class TestCreateStudent:

    def test_create_success(self, client, headers):
        resp = create_student(client, headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["roll_no"] == "CS001"
        assert data["name"] == "Alice"
        assert data["email"] == "alice@test.com"
        assert data["semester"] == 3
        assert "id" in data

    def test_create_duplicate_roll_no(self, client, headers):
        create_student(client, headers)
        resp = create_student(client, headers, email="alice2@test.com")  # same roll_no
        assert resp.status_code == 400
        assert resp.json()["detail"] == "Student already exists"

    def test_create_invalid_semester(self, client, headers):
        resp = client.post("/student/register", json={
            "roll_no": "CS999",
            "name": "Bob",
            "email": "bob@test.com",
            "semester": 15,  # out of range (gt=0, lt=10)
        }, headers=headers)
        assert resp.status_code == 422

    def test_create_without_auth(self, client, clean_db):
        resp = client.post("/student/register", json={
            "roll_no": "CS001",
            "name": "Alice",
            "email": "alice@test.com",
            "semester": 3,
        })
        assert resp.status_code == 401


# ── Get all students ──────────────────────────────────────────────────────────

class TestGetAllStudents:

    def test_get_all_empty(self, client, headers):
        resp = client.get("/student/all-students", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_all_returns_list(self, client, headers):
        create_student(client, headers, roll_no="CS001", email="s1@test.com")
        create_student(client, headers, roll_no="CS002", email="s2@test.com")
        resp = client.get("/student/all-students", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_all_without_auth(self, client, clean_db):
        resp = client.get("/student/all-students")
        assert resp.status_code == 401


# ── Get single student ────────────────────────────────────────────────────────

class TestGetStudent:

    def test_get_student_success(self, client, headers):
        create_student(client, headers)
        resp = client.get("/student/all-students", headers=headers)
        student_id = resp.json()[0]["id"]

        resp = client.get(f"/student/{student_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["roll_no"] == "CS001"

    def test_get_student_not_found(self, client, headers):
        resp = client.get("/student/999999", headers=headers)
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Student not found"

    def test_get_student_without_auth(self, client, clean_db):
        resp = client.get("/student/1")
        assert resp.status_code == 401


# ── Update student ────────────────────────────────────────────────────────────

class TestUpdateStudent:

    def test_update_name(self, client, headers):
        create_student(client, headers)
        student_id = client.get("/student/all-students", headers=headers).json()[0]["id"]

        resp = client.put(f"/student/{student_id}", json={"name": "Alice Updated"}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Alice Updated"
        assert resp.json()["email"] == "alice@test.com"  # unchanged

    def test_update_semester(self, client, headers):
        create_student(client, headers)
        student_id = client.get("/student/all-students", headers=headers).json()[0]["id"]

        resp = client.put(f"/student/{student_id}", json={"semester": 5}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["semester"] == 5

    def test_update_partial_fields(self, client, headers):
        """Only provided fields should change, others remain."""
        create_student(client, headers)
        student_id = client.get("/student/all-students", headers=headers).json()[0]["id"]

        resp = client.put(f"/student/{student_id}", json={"name": "New Name"}, headers=headers)
        data = resp.json()
        assert data["name"] == "New Name"
        assert data["semester"] == 3  # unchanged

    def test_update_not_found(self, client, headers):
        resp = client.put("/student/999999", json={"name": "Ghost"}, headers=headers)
        assert resp.status_code == 404

    def test_update_without_auth(self, client, clean_db):
        resp = client.put("/student/1", json={"name": "X"})
        assert resp.status_code == 401


# ── Delete student ────────────────────────────────────────────────────────────

class TestDeleteStudent:

    def test_delete_success(self, client, headers):
        create_student(client, headers)
        student_id = client.get("/student/all-students", headers=headers).json()[0]["id"]

        resp = client.delete(f"/student/{student_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["message"] == "Student deleted successfully"

        # Confirm it's gone
        resp = client.get(f"/student/{student_id}", headers=headers)
        assert resp.status_code == 404

    def test_delete_not_found(self, client, headers):
        resp = client.delete("/student/999999", headers=headers)
        assert resp.status_code == 404

    def test_delete_without_auth(self, client, clean_db):
        resp = client.delete("/student/1")
        assert resp.status_code == 401
