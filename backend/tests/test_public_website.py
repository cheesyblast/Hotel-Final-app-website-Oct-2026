"""Backend tests for public website endpoints (iteration 12)"""
import os
import time
import pytest
import requests
from datetime import datetime, timedelta

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://hospitality-ops-18.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api/public"


@pytest.fixture(scope="module")
def future_dates():
    today = datetime.now().date()
    ci = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    co = (today + timedelta(days=32)).strftime("%Y-%m-%d")
    return ci, co


class TestHotelInfo:
    def test_hotel_info(self):
        r = requests.get(f"{API}/hotel-info", timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert "hotel_name" in data
        assert "hotel_address" in data
        assert isinstance(data["hotel_name"], str)


class TestPublicRooms:
    def test_rooms_grouped(self):
        r = requests.get(f"{API}/rooms", timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        if data:
            room = data[0]
            for k in ["room_type", "price_per_night", "max_occupancy", "total_rooms"]:
                assert k in room


class TestAvailability:
    def test_availability_ok(self, future_dates):
        ci, co = future_dates
        r = requests.get(f"{API}/availability", params={"check_in": ci, "check_out": co}, timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert data["check_in"] == ci
        assert data["check_out"] == co
        assert data["nights"] == 2
        assert "available_room_types" in data
        if data["available_room_types"]:
            rt = data["available_room_types"][0]
            assert "total_price" in rt
            assert "available_count" in rt
            assert rt["total_price"] == rt["price_per_night"] * 2

    def test_availability_bad_dates(self):
        r = requests.get(f"{API}/availability", params={"check_in": "2027-01-10", "check_out": "2027-01-10"}, timeout=15)
        assert r.status_code == 400

    def test_availability_past(self):
        r = requests.get(f"{API}/availability", params={"check_in": "2020-01-01", "check_out": "2020-01-02"}, timeout=15)
        assert r.status_code == 400

    def test_availability_invalid_format(self):
        r = requests.get(f"{API}/availability", params={"check_in": "bad", "check_out": "2027-01-01"}, timeout=15)
        assert r.status_code == 400


@pytest.fixture(scope="module")
def hold_response(future_dates):
    ci, co = future_dates
    # First get a valid room type
    rooms_r = requests.get(f"{API}/availability", params={"check_in": ci, "check_out": co}, timeout=15)
    assert rooms_r.status_code == 200
    types = rooms_r.json().get("available_room_types", [])
    if not types:
        pytest.skip("No available room types")
    room_type = types[0]["room_type"]

    payload = {
        "room_type": room_type,
        "check_in": ci,
        "check_out": co,
        "guest_name": "TEST_WebGuest",
        "guest_email": "test_webguest@example.com",
        "guest_phone": "+94770000000",
        "country": "Sri Lanka",
        "num_guests": 2,
        "special_requests": "TEST",
        "payment_option": "advance",
    }
    r = requests.post(f"{API}/booking/hold", json=payload, timeout=15)
    assert r.status_code == 200, r.text
    return r.json(), payload


class TestBookingHold:
    def test_hold_fields(self, hold_response):
        data, _ = hold_response
        for k in ["hold_id", "order_id", "room_number", "nights", "payment_amount", "total_amount", "payhere", "expires_in_seconds"]:
            assert k in data
        assert data["expires_in_seconds"] == 300
        assert data["nights"] == 2
        # advance = 30%
        assert abs(data["payment_amount"] - round(data["total_amount"] * 0.30, 2)) < 0.01
        assert data["payhere"]["order_id"] == data["order_id"]

    def test_status_endpoint(self, hold_response):
        data, _ = hold_response
        r = requests.get(f"{API}/booking/status/{data['order_id']}", timeout=15)
        assert r.status_code == 200
        s = r.json()
        assert s["order_id"] == data["order_id"]
        assert s["status"] in ("held", "expired")

    def test_status_not_found(self):
        r = requests.get(f"{API}/booking/status/NOPE-12345", timeout=15)
        assert r.status_code == 404

    def test_hold_invalid_dates(self):
        payload = {
            "room_type": "Standard",
            "check_in": "2027-05-05",
            "check_out": "2027-05-05",
            "guest_name": "TEST",
            "guest_email": "t@t.com",
            "guest_phone": "123",
        }
        r = requests.post(f"{API}/booking/hold", json=payload, timeout=15)
        assert r.status_code == 400


class TestContactForm:
    def test_contact_submit(self):
        # Turnstile is likely configured; if secret is set & token is bogus, server returns 400.
        # The code allows pass when HTTP error; invalid token -> success=false -> 400.
        payload = {
            "name": "TEST_Contact",
            "email": "test_contact@example.com",
            "phone": "+94770000111",
            "message": "TEST message from automated test",
            "turnstile_token": "test-token",
        }
        r = requests.post(f"{API}/contact", json=payload, timeout=20)
        # Accept either 200 (no secret / bypass) or 400 (turnstile failure)
        assert r.status_code in (200, 400), r.text
        if r.status_code == 200:
            assert "message" in r.json()
