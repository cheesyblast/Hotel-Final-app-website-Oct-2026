"""
Test suite for Iteration 11 features:
1. Payroll - Create new employee works (POST /api/payroll/employees with hire_date)
2. Booking channel auto_rate toggle for commission auto-calculation
3. Dynamic income/expense categories (admin-addable)
4. Advance payment field in booking creation
5. Restaurant order creation
"""

import pytest
import requests
import os
from datetime import date, datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://hospitality-ops-18.preview.emergentagent.com')

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
        return response.json()["access_token"]
    
    def test_login_success(self):
        """Test admin login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "Admin"


class TestPayrollEmployeeCreation:
    """Test payroll employee creation with hire_date fix"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        return response.json()["access_token"]
    
    def test_create_employee_with_hire_date(self, auth_token):
        """Test creating employee with hire_date - verifies datetime.date MongoDB fix"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create a new employee with hire_date
        employee_data = {
            "employee_id": f"TEST_EMP_{datetime.now().strftime('%H%M%S')}",
            "first_name": "Test",
            "last_name": "Employee",
            "email": "test.employee@example.com",
            "phone": "0771234567",
            "nic": "123456789V",
            "address": "123 Test Street",
            "hire_date": date.today().isoformat(),  # This was failing before the fix
            "department": "Front Desk",
            "designation": "Staff",
            "employment_type": "Full-time",
            "basic_salary": 50000
        }
        
        response = requests.post(
            f"{BASE_URL}/api/payroll/employees",
            json=employee_data,
            headers=headers
        )
        
        # Should succeed now with the datetime.date fix
        assert response.status_code == 200, f"Employee creation failed: {response.text}"
        data = response.json()
        # Response has nested structure: {"message": "...", "employee": {...}}
        if "employee" in data:
            employee = data["employee"]
            assert employee["employee_id"] == employee_data["employee_id"]
            assert employee["first_name"] == "Test"
            assert employee["last_name"] == "Employee"
            assert "hire_date" in employee
            employee_id = employee["id"]
        else:
            assert data["employee_id"] == employee_data["employee_id"]
            employee_id = data["id"]
        
        # Cleanup - delete the test employee
        delete_response = requests.delete(
            f"{BASE_URL}/api/payroll/employees/{employee_id}",
            headers=headers
        )
        # Note: Delete may return 200 or 404 depending on implementation
    
    def test_get_employees(self, auth_token):
        """Test getting list of employees"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/payroll/employees",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestBookingChannelAutoRate:
    """Test booking channel auto_rate toggle"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        return response.json()["access_token"]
    
    def test_get_booking_channels(self, auth_token):
        """Test getting booking channels with auto_rate field"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/booking-channels",
            headers=headers
        )
        
        assert response.status_code == 200
        channels = response.json()
        assert isinstance(channels, list)
        
        # Check that channels have auto_rate field
        for channel in channels:
            assert "auto_rate" in channel, f"Channel {channel.get('channel_name')} missing auto_rate field"
    
    def test_create_channel_with_auto_rate(self, auth_token):
        """Test creating a booking channel with auto_rate toggle"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        channel_data = {
            "channel_name": f"TEST_Channel_{datetime.now().strftime('%H%M%S')}",
            "channel_type": "OTA",
            "commission_rate": 15.0,
            "auto_rate": True,  # Auto-calculate commission
            "contact_email": "test@channel.com",
            "contact_phone": "0771234567"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/booking-channels",
            json=channel_data,
            headers=headers
        )
        
        assert response.status_code == 200, f"Channel creation failed: {response.text}"
        data = response.json()
        assert data["channel_name"] == channel_data["channel_name"]
        assert data["auto_rate"] == True
        assert data["commission_rate"] == 15.0
        
        # Cleanup - delete the test channel
        channel_id = data["id"]
        requests.delete(f"{BASE_URL}/api/booking-channels/{channel_id}", headers=headers)
    
    def test_create_channel_with_auto_rate_off(self, auth_token):
        """Test creating a booking channel with auto_rate OFF"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        channel_data = {
            "channel_name": f"TEST_Manual_{datetime.now().strftime('%H%M%S')}",
            "channel_type": "Direct",
            "commission_rate": 10.0,
            "auto_rate": False,  # Manual commission entry
            "contact_email": "manual@channel.com"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/booking-channels",
            json=channel_data,
            headers=headers
        )
        
        assert response.status_code == 200, f"Channel creation failed: {response.text}"
        data = response.json()
        assert data["auto_rate"] == False
        
        # Cleanup
        channel_id = data["id"]
        requests.delete(f"{BASE_URL}/api/booking-channels/{channel_id}", headers=headers)


class TestDynamicCategories:
    """Test dynamic income/expense categories"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        return response.json()["access_token"]
    
    def test_get_expense_categories(self, auth_token):
        """Test getting expense categories"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/categories/expense",
            headers=headers
        )
        
        assert response.status_code == 200
        categories = response.json()
        assert isinstance(categories, list)
    
    def test_get_income_categories(self, auth_token):
        """Test getting income categories"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/categories/income",
            headers=headers
        )
        
        assert response.status_code == 200
        categories = response.json()
        assert isinstance(categories, list)
    
    def test_add_expense_category(self, auth_token):
        """Test adding a new expense category"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        category_name = f"TEST_Expense_{datetime.now().strftime('%H%M%S')}"
        
        # The API expects name in JSON body
        response = requests.post(
            f"{BASE_URL}/api/categories/expense",
            json={"name": category_name},
            headers=headers
        )
        
        assert response.status_code == 200, f"Add category failed: {response.text}"
        data = response.json()
        assert "added" in data["message"].lower() or category_name in data.get("name", "")
        
        # Verify it was added
        get_response = requests.get(
            f"{BASE_URL}/api/categories/expense",
            headers=headers
        )
        categories = get_response.json()
        assert category_name in categories
        
        # Cleanup - delete the test category
        requests.delete(
            f"{BASE_URL}/api/categories/expense/{category_name}",
            headers=headers
        )
    
    def test_add_income_category(self, auth_token):
        """Test adding a new income category"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        category_name = f"TEST_Income_{datetime.now().strftime('%H%M%S')}"
        
        # The API expects name in JSON body
        response = requests.post(
            f"{BASE_URL}/api/categories/income",
            json={"name": category_name},
            headers=headers
        )
        
        assert response.status_code == 200, f"Add category failed: {response.text}"
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/categories/income/{category_name}",
            headers=headers
        )


class TestBookingWithAdvancePayment:
    """Test booking creation with advance payment field"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        return response.json()["access_token"]
    
    def test_get_rooms(self, auth_token):
        """Test getting available rooms"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/rooms",
            headers=headers
        )
        
        assert response.status_code == 200
        rooms = response.json()
        assert isinstance(rooms, list)
        return rooms
    
    def test_create_booking_with_advance_payment(self, auth_token):
        """Test creating a booking with advance payment"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get available rooms first
        rooms_response = requests.get(f"{BASE_URL}/api/rooms", headers=headers)
        rooms = rooms_response.json()
        available_room = next((r for r in rooms if r.get("status") == "Available"), None)
        
        if not available_room:
            pytest.skip("No available rooms for booking test")
        
        # Create booking with advance payment - use unique dates to avoid conflicts
        check_in = (date.today() + timedelta(days=30)).isoformat()
        check_out = (date.today() + timedelta(days=32)).isoformat()
        
        booking_data = {
            "guest_name": f"TEST_Advance_{datetime.now().strftime('%H%M%S')}",
            "guest_email": "advance@test.com",
            "guest_phone": "0771234567",
            "guest_country": "Sri Lanka",
            "room_number": available_room["room_number"],
            "check_in_date": check_in,
            "check_out_date": check_out,
            "stay_type": "Night Stay",
            "booking_amount": 20000,
            "advance_amount": 5000,  # Advance payment
            "advance_payment_method": "Cash",
            "commission_amount": 0,
            "booking_channel_name": "Direct",
            "additional_notes": "Test booking with advance"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/bookings",
            json=booking_data,
            headers=headers
        )
        
        assert response.status_code == 200, f"Booking creation failed: {response.text}"
        data = response.json()
        assert "TEST_Advance" in data["guest_name"]
        assert data["advance_amount"] == 5000
        
        # Cleanup - cancel the booking
        booking_id = data["id"]
        requests.post(f"{BASE_URL}/api/cancel/{booking_id}", headers=headers)


class TestRestaurantOrders:
    """Test restaurant order creation"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        return response.json()["access_token"]
    
    def test_get_menu_items(self, auth_token):
        """Test getting menu items"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Correct endpoint is /api/restaurant/menu-items
        response = requests.get(
            f"{BASE_URL}/api/restaurant/menu-items",
            headers=headers
        )
        
        assert response.status_code == 200
        items = response.json()
        assert isinstance(items, list)
    
    def test_get_restaurant_orders(self, auth_token):
        """Test getting restaurant orders"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/restaurant/orders",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "orders" in data or isinstance(data, list)
    
    def test_create_restaurant_order(self, auth_token):
        """Test creating a restaurant order"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get menu items first - correct endpoint
        menu_response = requests.get(f"{BASE_URL}/api/restaurant/menu-items", headers=headers)
        menu_items = menu_response.json()
        
        if not menu_items or len(menu_items) == 0:
            pytest.skip("No menu items available for order test")
        
        # Create order with first menu item
        first_item = menu_items[0]
        
        order_data = {
            "order_type": "table",
            "table_id": None,
            "room_number": None,
            "customer_name": f"TEST_Order_{datetime.now().strftime('%H%M%S')}",
            "items": [
                {
                    "menu_item_id": first_item["id"],
                    "menu_item_name": first_item["name"],
                    "quantity": 2,
                    "unit_price": first_item["price"],
                    "total_price": first_item["price"] * 2,
                    "special_notes": ""
                }
            ],
            "notes": "Test order",
            "service_charge_rate": 10.0
        }
        
        response = requests.post(
            f"{BASE_URL}/api/restaurant/orders",
            json=order_data,
            headers=headers
        )
        
        assert response.status_code == 200, f"Order creation failed: {response.text}"
        data = response.json()
        assert "TEST_Order" in data["customer_name"]
        assert len(data["items"]) == 1


class TestIncomeExpenseDefaultDate:
    """Test income/expense forms default to current date"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        return response.json()["access_token"]
    
    def test_create_expense_with_current_date(self, auth_token):
        """Test creating expense with current date"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        today = date.today().isoformat()
        
        expense_data = {
            "description": "TEST_Expense_Item",
            "amount": 1000,
            "category": "Utilities",
            "payment_method": "Cash",
            "expense_date": today  # Current date
        }
        
        response = requests.post(
            f"{BASE_URL}/api/expenses",
            json=expense_data,
            headers=headers
        )
        
        assert response.status_code == 200, f"Expense creation failed: {response.text}"
        data = response.json()
        assert data["description"] == "TEST_Expense_Item"
        # Date should be stored correctly
        assert today in data.get("expense_date", "")
    
    def test_create_income_with_current_date(self, auth_token):
        """Test creating income with current date"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        today = date.today().isoformat()
        
        income_data = {
            "description": "TEST_Income_Item",
            "amount": 5000,
            "category": "Restaurant Sales",
            "payment_method": "Cash",
            "income_date": today,  # Current date
            "guest_name": ""
        }
        
        response = requests.post(
            f"{BASE_URL}/api/incomes",
            json=income_data,
            headers=headers
        )
        
        assert response.status_code == 200, f"Income creation failed: {response.text}"
        data = response.json()
        assert data["description"] == "TEST_Income_Item"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
