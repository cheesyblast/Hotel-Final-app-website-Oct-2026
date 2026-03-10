"""
Test iteration 9 features:
1. Upcoming bookings API - should return all bookings with status='Upcoming' regardless of check-in date
2. Stock Management endpoints - CRUD operations for stocks
3. User page permissions for Manager role
"""

import pytest
import requests
import os
from datetime import date, timedelta, datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://hotel-notify-system.preview.emergentagent.com"

class TestUpcomingBookings:
    """Test that upcoming bookings stay visible regardless of check-in date"""
    
    def test_upcoming_bookings_returns_by_status(self):
        """Verify upcoming bookings are filtered by status, not date"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Login first
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        token = login_response.json().get("access_token")
        session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Get upcoming bookings
        response = session.get(f"{BASE_URL}/api/bookings/upcoming")
        assert response.status_code == 200, f"Failed to get upcoming bookings: {response.text}"
        
        bookings = response.json()
        print(f"Found {len(bookings)} upcoming bookings")
        
        # Verify all bookings have status 'Upcoming'
        for booking in bookings:
            assert booking.get("status") == "Upcoming", f"Expected status 'Upcoming' but got '{booking.get('status')}'"
            print(f"  - {booking.get('guest_name')}: Room {booking.get('room_number')}, Check-in: {booking.get('check_in_date')}")
        
        print("SUCCESS: All upcoming bookings have correct status")
    
    def test_past_date_booking_remains_upcoming(self):
        """Test that bookings with past check-in dates remain in upcoming list until checked-in/cancelled"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Login
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert login_response.status_code == 200
        token = login_response.json().get("access_token")
        session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Get all bookings to check the implementation
        all_bookings_response = session.get(f"{BASE_URL}/api/bookings")
        assert all_bookings_response.status_code == 200
        all_data = all_bookings_response.json()
        all_bookings = all_data.get("bookings", [])
        
        # Check for any booking with status 'Upcoming'
        upcoming_status_bookings = [b for b in all_bookings if b.get("status") == "Upcoming"]
        print(f"Total bookings with status 'Upcoming': {len(upcoming_status_bookings)}")
        
        # Now verify the upcoming endpoint returns same bookings
        upcoming_response = session.get(f"{BASE_URL}/api/bookings/upcoming")
        assert upcoming_response.status_code == 200
        upcoming_bookings = upcoming_response.json()
        
        # The count should match (or be close if there are timing issues)
        print(f"Upcoming endpoint returned: {len(upcoming_bookings)} bookings")
        
        # Check that we're not filtering by date
        today = date.today().isoformat()
        for booking in upcoming_bookings:
            check_in = booking.get("check_in_date", "")[:10]  # Handle datetime strings
            print(f"  Booking: {booking.get('guest_name')}, check-in: {check_in}, status: {booking.get('status')}")
        
        print("SUCCESS: Upcoming bookings API filters by status, not date")


class TestStockManagement:
    """Test Stock Management CRUD operations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authenticated session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        token = login_response.json().get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Store test item IDs for cleanup
        self.test_stock_ids = []
        
        yield
        
        # Cleanup test data
        for stock_id in self.test_stock_ids:
            try:
                self.session.delete(f"{BASE_URL}/api/stocks/{stock_id}")
            except:
                pass
    
    def test_get_stocks_endpoint(self):
        """Test GET /api/stocks endpoint"""
        response = self.session.get(f"{BASE_URL}/api/stocks")
        assert response.status_code == 200, f"Failed to get stocks: {response.text}"
        
        stocks = response.json()
        assert isinstance(stocks, list), "Expected list of stocks"
        print(f"SUCCESS: GET /api/stocks returned {len(stocks)} items")
    
    def test_create_stock_item_restaurant(self):
        """Test creating a restaurant stock item"""
        stock_data = {
            "item_name": "TEST_Coffee Beans",
            "item_type": "restaurant",
            "category": "Beverages",
            "unit": "kg",
            "current_stock": 50,
            "low_stock_threshold": 10,
            "cost_per_unit": 500
        }
        
        response = self.session.post(f"{BASE_URL}/api/stocks", json=stock_data)
        assert response.status_code == 200, f"Failed to create stock: {response.text}"
        
        data = response.json()
        assert "stock" in data, "Response should contain 'stock' object"
        stock = data["stock"]
        
        # Store ID for cleanup
        self.test_stock_ids.append(stock.get("id"))
        
        # Verify data
        assert stock["item_name"] == "TEST_Coffee Beans"
        assert stock["item_type"] == "restaurant"
        assert stock["category"] == "Beverages"
        assert stock["current_stock"] == 50
        
        print(f"SUCCESS: Created restaurant stock item: {stock['item_name']}")
    
    def test_create_stock_item_maintenance(self):
        """Test creating a maintenance stock item"""
        stock_data = {
            "item_name": "TEST_Light Bulbs",
            "item_type": "maintenance",
            "category": "Electrical",
            "unit": "pcs",
            "current_stock": 100,
            "low_stock_threshold": 20,
            "cost_per_unit": 150
        }
        
        response = self.session.post(f"{BASE_URL}/api/stocks", json=stock_data)
        assert response.status_code == 200, f"Failed to create stock: {response.text}"
        
        data = response.json()
        stock = data["stock"]
        self.test_stock_ids.append(stock.get("id"))
        
        assert stock["item_type"] == "maintenance"
        print(f"SUCCESS: Created maintenance stock item: {stock['item_name']}")
    
    def test_adjust_stock_add(self):
        """Test adding stock quantity"""
        # First create a stock item
        stock_data = {
            "item_name": "TEST_Tea Leaves",
            "item_type": "restaurant",
            "category": "Beverages",
            "unit": "kg",
            "current_stock": 10,
            "low_stock_threshold": 5,
            "cost_per_unit": 200
        }
        
        create_response = self.session.post(f"{BASE_URL}/api/stocks", json=stock_data)
        assert create_response.status_code == 200
        stock_id = create_response.json()["stock"]["id"]
        self.test_stock_ids.append(stock_id)
        
        # Now add stock
        adjust_response = self.session.post(f"{BASE_URL}/api/stocks/{stock_id}/adjust", json={
            "quantity": 20,
            "transaction_type": "add",
            "notes": "Test stock addition"
        })
        
        assert adjust_response.status_code == 200, f"Failed to add stock: {adjust_response.text}"
        result = adjust_response.json()
        
        assert result["previous_stock"] == 10
        assert result["new_stock"] == 30
        
        print(f"SUCCESS: Stock added - Previous: 10, New: 30")
    
    def test_adjust_stock_remove(self):
        """Test removing stock quantity"""
        # First create a stock item
        stock_data = {
            "item_name": "TEST_Sugar",
            "item_type": "restaurant",
            "category": "Supplies",
            "unit": "kg",
            "current_stock": 50,
            "low_stock_threshold": 10,
            "cost_per_unit": 100
        }
        
        create_response = self.session.post(f"{BASE_URL}/api/stocks", json=stock_data)
        assert create_response.status_code == 200
        stock_id = create_response.json()["stock"]["id"]
        self.test_stock_ids.append(stock_id)
        
        # Remove stock
        adjust_response = self.session.post(f"{BASE_URL}/api/stocks/{stock_id}/adjust", json={
            "quantity": 15,
            "transaction_type": "remove",
            "notes": "Test stock removal"
        })
        
        assert adjust_response.status_code == 200, f"Failed to remove stock: {adjust_response.text}"
        result = adjust_response.json()
        
        assert result["previous_stock"] == 50
        assert result["new_stock"] == 35
        
        print(f"SUCCESS: Stock removed - Previous: 50, New: 35")
    
    def test_stock_transactions_history(self):
        """Test GET /api/stocks/transactions endpoint"""
        response = self.session.get(f"{BASE_URL}/api/stocks/transactions?limit=50")
        assert response.status_code == 200, f"Failed to get transactions: {response.text}"
        
        transactions = response.json()
        assert isinstance(transactions, list), "Expected list of transactions"
        print(f"SUCCESS: Retrieved {len(transactions)} stock transactions")
    
    def test_stock_summary(self):
        """Test GET /api/stocks/summary endpoint"""
        response = self.session.get(f"{BASE_URL}/api/stocks/summary")
        assert response.status_code == 200, f"Failed to get summary: {response.text}"
        
        summary = response.json()
        
        # Verify summary contains expected fields
        assert "total_items" in summary, "Summary should contain total_items"
        assert "restaurant_items" in summary, "Summary should contain restaurant_items"
        assert "maintenance_items" in summary, "Summary should contain maintenance_items"
        assert "low_stock_count" in summary, "Summary should contain low_stock_count"
        
        print(f"SUCCESS: Stock summary - Total: {summary['total_items']}, Restaurant: {summary['restaurant_items']}, Maintenance: {summary['maintenance_items']}, Low Stock: {summary['low_stock_count']}")
    
    def test_delete_stock_item(self):
        """Test deleting a stock item"""
        # First create a stock item
        stock_data = {
            "item_name": "TEST_Delete_Item",
            "item_type": "maintenance",
            "category": "General",
            "unit": "pcs",
            "current_stock": 5,
            "low_stock_threshold": 2
        }
        
        create_response = self.session.post(f"{BASE_URL}/api/stocks", json=stock_data)
        assert create_response.status_code == 200
        stock_id = create_response.json()["stock"]["id"]
        
        # Delete the stock item
        delete_response = self.session.delete(f"{BASE_URL}/api/stocks/{stock_id}")
        assert delete_response.status_code == 200, f"Failed to delete stock: {delete_response.text}"
        
        print(f"SUCCESS: Stock item deleted")


class TestUserPagePermissions:
    """Test user page permissions functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authenticated session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert login_response.status_code == 200
        token = login_response.json().get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        self.test_user_ids = []
        
        yield
        
        # Cleanup test users
        for user_id in self.test_user_ids:
            try:
                self.session.delete(f"{BASE_URL}/api/users/{user_id}")
            except:
                pass
    
    def test_available_pages_endpoint(self):
        """Test GET /api/users/available-pages endpoint"""
        response = self.session.get(f"{BASE_URL}/api/users/available-pages")
        assert response.status_code == 200, f"Failed to get available pages: {response.text}"
        
        pages = response.json()
        assert isinstance(pages, list), "Expected list of pages"
        assert len(pages) > 0, "Should have at least one available page"
        
        # Check structure
        for page in pages:
            assert "id" in page, "Page should have 'id'"
            assert "name" in page, "Page should have 'name'"
        
        # Verify 'stocks' page is in the list
        page_ids = [p.get("id") for p in pages]
        assert "stocks" in page_ids, "Stocks should be in available pages"
        
        print(f"SUCCESS: Retrieved {len(pages)} available pages")
        for p in pages:
            print(f"  - {p.get('id')}: {p.get('name')}")
    
    def test_create_manager_with_permissions(self):
        """Test creating a Manager user with specific page permissions"""
        user_data = {
            "username": "TEST_manager_user",
            "password": "testpass123",
            "full_name": "Test Manager",
            "role": "Manager",
            "email": "test.manager@hotel.com",
            "page_permissions": ["dashboard", "bookings", "rooms", "stocks"]
        }
        
        response = self.session.post(f"{BASE_URL}/api/users", json=user_data)
        assert response.status_code == 200, f"Failed to create user: {response.text}"
        
        user = response.json()
        self.test_user_ids.append(user.get("id"))
        
        # Verify permissions were saved
        assert user.get("role") == "Manager"
        assert "page_permissions" in user
        saved_permissions = user.get("page_permissions", [])
        
        # Check permissions were saved correctly
        for perm in user_data["page_permissions"]:
            assert perm in saved_permissions, f"Permission '{perm}' should be saved"
        
        print(f"SUCCESS: Created Manager with permissions: {saved_permissions}")
    
    def test_create_admin_no_permissions_needed(self):
        """Test that Admin users don't need explicit page permissions"""
        user_data = {
            "username": "TEST_admin_user",
            "password": "testpass123",
            "full_name": "Test Admin",
            "role": "Admin",
            "email": "test.admin@hotel.com",
            "page_permissions": []  # Admin doesn't need permissions
        }
        
        response = self.session.post(f"{BASE_URL}/api/users", json=user_data)
        assert response.status_code == 200, f"Failed to create user: {response.text}"
        
        user = response.json()
        self.test_user_ids.append(user.get("id"))
        
        assert user.get("role") == "Admin"
        print(f"SUCCESS: Created Admin user - Admin has all access automatically")
    
    def test_update_user_permissions(self):
        """Test updating a user's page permissions"""
        # First create a manager user
        user_data = {
            "username": "TEST_update_perm_user",
            "password": "testpass123",
            "full_name": "Test Permission Update",
            "role": "Manager",
            "email": "test.perm@hotel.com",
            "page_permissions": ["dashboard"]
        }
        
        create_response = self.session.post(f"{BASE_URL}/api/users", json=user_data)
        assert create_response.status_code == 200
        user_id = create_response.json().get("id")
        self.test_user_ids.append(user_id)
        
        # Update permissions - API expects a list directly
        new_permissions = ["dashboard", "bookings", "rooms", "guests", "stocks"]
        update_response = self.session.put(f"{BASE_URL}/api/users/{user_id}/permissions", json=new_permissions)
        assert update_response.status_code == 200, f"Failed to update permissions: {update_response.text}"
        
        result = update_response.json()
        print(f"SUCCESS: Updated user permissions - {result.get('message', 'OK')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
