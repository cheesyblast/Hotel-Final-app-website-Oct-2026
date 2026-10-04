"""
Tests for iteration 11:
- Login returns page_permissions
- available-pages excludes 'reports'
- Create restricted user and verify permission storage
- Restricted user login returns limited page_permissions
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://hospitality-ops-18.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def admin_token():
    r = requests.post(f"{API}/auth/login", json={"username": "admin", "password": "admin123"})
    assert r.status_code == 200, f"Admin login failed: {r.text}"
    return r.json()["access_token"]


@pytest.fixture(scope="module")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


# ---------- Login & page_permissions ----------
def test_admin_login_returns_page_permissions():
    r = requests.post(f"{API}/auth/login", json={"username": "admin", "password": "admin123"})
    assert r.status_code == 200
    data = r.json()
    assert "user" in data
    assert "page_permissions" in data["user"], "Login must return page_permissions"
    assert isinstance(data["user"]["page_permissions"], list)
    assert data["user"]["role"] == "Admin"


# ---------- available-pages excludes reports ----------
def test_available_pages_excludes_reports(admin_headers):
    r = requests.get(f"{API}/users/available-pages", headers=admin_headers)
    assert r.status_code == 200
    pages = r.json()
    page_ids = [p["id"] for p in pages]
    assert "reports" not in page_ids, f"'reports' should not be in available pages: {page_ids}"
    # core pages still present
    for p in ["dashboard", "rooms", "bookings", "settings", "income_expense"]:
        assert p in page_ids


# ---------- Create restricted user and verify permissions ----------
@pytest.fixture(scope="module")
def restricted_user(admin_headers):
    # Cleanup first if exists
    users_resp = requests.get(f"{API}/users", headers=admin_headers)
    if users_resp.status_code == 200:
        for u in users_resp.json():
            if u.get("username") == "permtest":
                requests.delete(f"{API}/users/{u['id']}", headers=admin_headers)
    payload = {
        "username": "permtest",
        "password": "permtest123",
        "full_name": "Perm Test",
        "role": "Staff",
        "email": "permtest@test.com",
        "page_permissions": ["dashboard", "rooms", "bookings"],
    }
    r = requests.post(f"{API}/users", json=payload, headers=admin_headers)
    assert r.status_code in (200, 201), f"Create user failed: {r.status_code} {r.text}"
    user = r.json()
    yield user
    # Teardown
    uid = user.get("id")
    if uid:
        requests.delete(f"{API}/users/{uid}", headers=admin_headers)


def test_create_restricted_user(restricted_user):
    assert restricted_user["username"] == "permtest"
    assert restricted_user["role"] == "Staff"
    assert set(restricted_user.get("page_permissions", [])) == {"dashboard", "rooms", "bookings"}


def test_restricted_user_login_returns_limited_permissions(restricted_user):
    r = requests.post(f"{API}/auth/login", json={"username": "permtest", "password": "permtest123"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert "user" in data
    perms = data["user"].get("page_permissions")
    assert perms is not None
    assert set(perms) == {"dashboard", "rooms", "bookings"}
    assert data["user"]["role"] == "Staff"


def test_restricted_user_token_works(restricted_user):
    r = requests.post(f"{API}/auth/login", json={"username": "permtest", "password": "permtest123"})
    token = r.json()["access_token"]
    me = requests.get(f"{API}/auth/me", headers={"Authorization": f"Bearer {token}"})
    # /auth/me may or may not exist - check 200 or skip
    if me.status_code == 404:
        pytest.skip("/auth/me not implemented")
    assert me.status_code == 200
