"""
Backend tests for new features:
1. Calendar view API - /api/bookings
2. Channel API Settings - GET/PUT /api/channel-api-settings
3. Reports endpoints for PDF export
"""
import pytest
import requests
import os
from datetime import datetime, date, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')


class TestAuth:
    """Authentication tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_login_success(self):
        """Test successful login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        print("✓ Login successful")


class TestCalendarAPI:
    """Tests for Calendar view - uses /api/bookings endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authentication token and headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        token = response.json().get("access_token")
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def test_get_bookings_for_calendar(self, auth_headers):
        """Test GET /api/bookings - used by CalendarView component"""
        response = requests.get(f"{BASE_URL}/api/bookings", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Response should have 'bookings' key (paginated response)
        assert "bookings" in data or isinstance(data, list)
        print(f"✓ Bookings endpoint returns data: {len(data.get('bookings', data))} bookings")
    
    def test_get_rooms_for_calendar(self, auth_headers):
        """Test GET /api/rooms - used by CalendarView for room count"""
        response = requests.get(f"{BASE_URL}/api/rooms", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Rooms endpoint returns {len(data)} rooms")


class TestChannelAPISettings:
    """Tests for Channel API Settings - Booking.com, Expedia, Agoda"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authentication token and headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        token = response.json().get("access_token")
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def test_get_channel_api_settings(self, auth_headers):
        """Test GET /api/channel-api-settings"""
        response = requests.get(f"{BASE_URL}/api/channel-api-settings", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Check expected fields exist for all 3 OTA channels
        assert "booking_com_api_key" in data
        assert "booking_com_property_id" in data
        assert "booking_com_enabled" in data
        assert "expedia_api_key" in data
        assert "expedia_property_id" in data
        assert "expedia_enabled" in data
        assert "agoda_api_key" in data
        assert "agoda_property_id" in data
        assert "agoda_enabled" in data
        print("✓ Channel API settings structure is correct")
    
    def test_update_channel_api_settings(self, auth_headers):
        """Test PUT /api/channel-api-settings"""
        # Update settings
        test_settings = {
            "booking_com_enabled": True,
            "booking_com_api_key": "TEST_BOOKING_COM_KEY",
            "booking_com_property_id": "TEST_PROP_123",
            "expedia_enabled": False,
            "agoda_enabled": False
        }
        
        response = requests.put(
            f"{BASE_URL}/api/channel-api-settings",
            headers=auth_headers,
            json=test_settings
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("message") == "Settings updated successfully"
        print("✓ Channel API settings updated successfully")
        
        # Verify the update persisted
        verify_response = requests.get(f"{BASE_URL}/api/channel-api-settings", headers=auth_headers)
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data.get("booking_com_enabled") == True
        assert verify_data.get("booking_com_api_key") == "TEST_BOOKING_COM_KEY"
        assert verify_data.get("booking_com_property_id") == "TEST_PROP_123"
        print("✓ Channel API settings verified after update")
    
    def test_update_all_channel_settings(self, auth_headers):
        """Test updating all 3 channel settings"""
        test_settings = {
            "booking_com_enabled": True,
            "booking_com_api_key": "BOOKING_KEY_123",
            "booking_com_property_id": "BOOKING_PROP_456",
            "expedia_enabled": True,
            "expedia_api_key": "EXPEDIA_KEY_789",
            "expedia_property_id": "EXPEDIA_PROP_012",
            "agoda_enabled": True,
            "agoda_api_key": "AGODA_KEY_345",
            "agoda_property_id": "AGODA_PROP_678"
        }
        
        response = requests.put(
            f"{BASE_URL}/api/channel-api-settings",
            headers=auth_headers,
            json=test_settings
        )
        assert response.status_code == 200
        
        # Verify all settings
        verify_response = requests.get(f"{BASE_URL}/api/channel-api-settings", headers=auth_headers)
        verify_data = verify_response.json()
        
        assert verify_data.get("booking_com_enabled") == True
        assert verify_data.get("expedia_enabled") == True
        assert verify_data.get("agoda_enabled") == True
        print("✓ All 3 channel settings (Booking.com, Expedia, Agoda) updated and verified")


class TestReportsAPI:
    """Tests for Reports endpoints (Daily/Monthly reports for PDF export)"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authentication token and headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        token = response.json().get("access_token")
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def test_get_daily_report(self, auth_headers):
        """Test GET /api/reports/daily - used for Daily Report PDF"""
        today = date.today().isoformat()
        response = requests.get(
            f"{BASE_URL}/api/reports/daily?date={today}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        # Check expected fields for daily report
        assert "date" in data
        assert "revenue" in data or "total_revenue" in data
        print(f"✓ Daily report endpoint works for date: {today}")
    
    def test_get_monthly_report(self, auth_headers):
        """Test GET /api/reports/monthly - used for Monthly Report PDF"""
        current_month = date.today().replace(day=1).isoformat()
        response = requests.get(
            f"{BASE_URL}/api/reports/monthly?month={current_month}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        # Check expected structure
        assert isinstance(data, dict) or isinstance(data, list)
        print(f"✓ Monthly report endpoint works for month: {current_month}")


class TestBookingCreation:
    """Tests for booking creation with country field (datalist feature)"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authentication token and headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        token = response.json().get("access_token")
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def test_create_booking_with_country(self, auth_headers):
        """Test creating a booking with country field"""
        # First get an available room
        rooms_response = requests.get(f"{BASE_URL}/api/rooms", headers=auth_headers)
        rooms = rooms_response.json()
        available_room = next((r for r in rooms if r.get("status") == "Available"), None)
        
        if not available_room:
            pytest.skip("No available rooms for booking test")
        
        # Create booking with country
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        booking_data = {
            "guest_name": "TEST_CountryGuest",
            "guest_email": "test@example.com",
            "guest_phone": "+1234567890",
            "guest_country": "Sri Lanka",  # Testing country field
            "room_number": available_room.get("room_number"),
            "check_in_date": today.isoformat(),
            "check_out_date": tomorrow.isoformat(),
            "booking_amount": 5000,
            "booking_channel_name": "Direct"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/bookings",
            headers=auth_headers,
            json=booking_data
        )
        
        assert response.status_code in [200, 201], f"Failed to create booking: {response.text}"
        data = response.json()
        assert data.get("guest_name") == "TEST_CountryGuest"
        print(f"✓ Booking created with country field: {booking_data['guest_country']}")
        
        # Clean up - cancel the test booking
        booking_id = data.get("id")
        if booking_id:
            requests.post(f"{BASE_URL}/api/cancel/{booking_id}", headers=auth_headers)
            print("✓ Test booking cleaned up")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
