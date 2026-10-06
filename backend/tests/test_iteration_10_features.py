"""
Test Suite for Iteration 10 Features:
1. PDF upload for passport/ID in booking form
2. Guest details modal - view details works for all guests (including without email)
3. Restaurant menu item dropdown with Edit/Delete options
4. Menu item delete check - blocks delete if used in orders
5. Room change during check-in
"""

import pytest
import requests
import os
import base64

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"


class TestAuth:
    """Authentication tests"""
    
    def test_login_success(self):
        """Test admin login and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        print("✅ Login successful")


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for tests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip("Cannot authenticate for tests")
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestPDFUploadInBooking:
    """Test PDF upload feature for passport/ID in booking form"""
    
    def test_create_booking_with_id_proof(self, auth_headers):
        """Test creating a booking with PDF ID proof"""
        # Create a small dummy PDF (base64 encoded)
        # This is a minimal valid PDF
        dummy_pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Count 0 /Kids [] >>\nendobj\nxref\n0 3\n0000000000 65535 f \n0000000009 00000 n \n0000000052 00000 n \ntrailer\n<< /Root 1 0 R /Size 3 >>\nstartxref\n101\n%%EOF"
        dummy_pdf_base64 = base64.b64encode(dummy_pdf_content).decode('utf-8')
        
        # Get an available room first
        rooms_resp = requests.get(f"{BASE_URL}/api/rooms", headers=auth_headers)
        available_rooms = [r for r in rooms_resp.json() if r.get('status') == 'Available']
        
        if not available_rooms:
            pytest.skip("No available rooms for testing")
        
        room_number = available_rooms[0]['room_number']
        
        booking_data = {
            "guest_name": "TEST_PDFProofGuest",
            "guest_email": "pdftest@example.com",
            "guest_phone": "+94771234567",
            "guest_country": "Sri Lanka",
            "guest_id_passport": "NP12345678",
            "guest_id_proof": dummy_pdf_base64,
            "guest_id_proof_filename": "test_passport.pdf",
            "room_number": room_number,
            "check_in_date": "2026-02-15",
            "check_out_date": "2026-02-17",
            "stay_type": "Night Stay",
            "booking_amount": 15000,
            "additional_notes": "Test booking with PDF proof"
        }
        
        response = requests.post(f"{BASE_URL}/api/bookings", json=booking_data, headers=auth_headers)
        assert response.status_code == 200, f"Failed to create booking: {response.text}"
        
        data = response.json()
        assert data.get('guest_name') == "TEST_PDFProofGuest"
        print("✅ Booking created with PDF proof")
        
        # Verify the proof is stored
        guest_resp = requests.get(f"{BASE_URL}/api/guests/pdftest@example.com", headers=auth_headers)
        assert guest_resp.status_code == 200, f"Failed to get guest: {guest_resp.text}"
        guest_data = guest_resp.json()
        assert guest_data.get('id_proof'), "ID proof should be stored"
        assert guest_data.get('id_proof_filename') == "test_passport.pdf"
        print("✅ PDF proof stored correctly in guest record")


class TestGuestDetailsForAllGuests:
    """Test that View Details works for all guests including those without email"""
    
    def test_create_guest_without_email(self, auth_headers):
        """Create a guest without email for testing"""
        # Get available room
        rooms_resp = requests.get(f"{BASE_URL}/api/rooms", headers=auth_headers)
        available_rooms = [r for r in rooms_resp.json() if r.get('status') == 'Available']
        
        if not available_rooms:
            pytest.skip("No available rooms for testing")
        
        room_number = available_rooms[0]['room_number']
        
        # Create booking without email (like Anushan)
        booking_data = {
            "guest_name": "TEST_NoEmailGuest",
            "guest_email": "",  # No email
            "guest_phone": "+94999888777",
            "guest_country": "India",
            "room_number": room_number,
            "check_in_date": "2026-02-20",
            "check_out_date": "2026-02-22",
            "stay_type": "Night Stay",
            "booking_amount": 10000
        }
        
        response = requests.post(f"{BASE_URL}/api/bookings", json=booking_data, headers=auth_headers)
        assert response.status_code == 200, f"Failed to create no-email booking: {response.text}"
        
        booking = response.json()
        assert booking.get('guest_name') == "TEST_NoEmailGuest"
        print(f"✅ Created guest without email, booking ID: {booking.get('id')}")
        return booking.get('id')
    
    def test_get_guest_details_with_email(self, auth_headers):
        """Test getting guest details using email identifier"""
        # Use the PDF test guest we created earlier
        response = requests.get(f"{BASE_URL}/api/guests/pdftest@example.com", headers=auth_headers)
        
        if response.status_code == 404:
            pytest.skip("PDF test guest not found")
        
        assert response.status_code == 200, f"Failed to get guest by email: {response.text}"
        data = response.json()
        assert data.get('name') == "TEST_PDFProofGuest"
        assert data.get('email') == "pdftest@example.com"
        assert 'bookings' in data
        print("✅ Guest details retrieved by email")
    
    def test_get_guest_details_without_email(self, auth_headers):
        """Test getting guest details using composite key (for guests without email)"""
        # First get all guests to find one without email
        guests_resp = requests.get(f"{BASE_URL}/api/guests", headers=auth_headers)
        assert guests_resp.status_code == 200
        
        guests = guests_resp.json()
        no_email_guest = None
        for g in guests:
            if not g.get('email') or g.get('email') == '':
                no_email_guest = g
                break
        
        if not no_email_guest:
            # Check for guests with 'Not provided' email
            for g in guests:
                if g.get('email') == 'Not provided':
                    no_email_guest = g
                    break
        
        if not no_email_guest:
            pytest.skip("No guest without email found")
        
        # Get the guest ID (should be composite: name_phone_bookingId format)
        guest_id = no_email_guest.get('id')
        assert guest_id, "Guest should have an id"
        
        # Fetch guest details using the composite ID
        response = requests.get(f"{BASE_URL}/api/guests/{guest_id}", headers=auth_headers)
        assert response.status_code == 200, f"Failed to get guest without email: {response.text}"
        
        data = response.json()
        assert 'name' in data
        assert 'bookings' in data
        print(f"✅ Guest without email retrieved successfully: {data.get('name')}")


class TestMenuItemEditAndDelete:
    """Test restaurant menu item Edit and Delete functionality"""
    
    def test_get_menu_items(self, auth_headers):
        """Get existing menu items"""
        response = requests.get(f"{BASE_URL}/api/restaurant/menu-items", headers=auth_headers)
        assert response.status_code == 200, f"Failed to get menu items: {response.text}"
        print(f"✅ Retrieved {len(response.json())} menu items")
        return response.json()
    
    def test_create_test_menu_item(self, auth_headers):
        """Create a test menu item for edit testing"""
        # First get categories
        cat_resp = requests.get(f"{BASE_URL}/api/restaurant/categories", headers=auth_headers)
        categories = cat_resp.json()
        
        if not categories:
            # Create a category first
            cat_data = {"name": "TEST_Category", "description": "Test category", "display_order": 99}
            cat_resp = requests.post(f"{BASE_URL}/api/restaurant/categories", json=cat_data, headers=auth_headers)
            category_id = cat_resp.json().get('id')
        else:
            category_id = categories[0]['id']
        
        # Create a test menu item
        item_data = {
            "name": "TEST_MenuItem",
            "description": "Test item for edit testing",
            "price": 250.00,
            "category_id": category_id,
            "is_vegetarian": False,
            "is_spicy": True,
            "prep_time": 10
        }
        
        response = requests.post(f"{BASE_URL}/api/restaurant/menu-items", json=item_data, headers=auth_headers)
        assert response.status_code == 200, f"Failed to create menu item: {response.text}"
        
        data = response.json()
        assert data.get('name') == "TEST_MenuItem"
        print(f"✅ Created test menu item: {data.get('id')}")
        return data
    
    def test_edit_menu_item(self, auth_headers):
        """Test editing a menu item"""
        # Get menu items
        items_resp = requests.get(f"{BASE_URL}/api/restaurant/menu-items", headers=auth_headers)
        items = items_resp.json()
        
        # Find our test item
        test_item = next((i for i in items if i['name'] == 'TEST_MenuItem'), None)
        
        if not test_item:
            pytest.skip("Test menu item not found")
        
        item_id = test_item['id']
        
        # Edit the item
        update_data = {
            "name": "TEST_MenuItem_Updated",
            "description": "Updated description",
            "price": 300.00,
            "is_vegetarian": True
        }
        
        response = requests.put(f"{BASE_URL}/api/restaurant/menu-items/{item_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200, f"Failed to edit menu item: {response.text}"
        
        updated = response.json()
        assert updated.get('name') == "TEST_MenuItem_Updated"
        assert updated.get('price') == 300.00
        assert updated.get('is_vegetarian') == True
        print("✅ Menu item edited successfully")
    
    def test_check_menu_item_deletable_no_orders(self, auth_headers):
        """Test can-delete check for item with no orders"""
        # Get menu items
        items_resp = requests.get(f"{BASE_URL}/api/restaurant/menu-items", headers=auth_headers)
        items = items_resp.json()
        
        # Find our test item
        test_item = next((i for i in items if 'TEST_MenuItem' in i['name']), None)
        
        if not test_item:
            pytest.skip("Test menu item not found")
        
        item_id = test_item['id']
        
        # Check if deletable
        response = requests.get(f"{BASE_URL}/api/restaurant/menu-items/{item_id}/can-delete", headers=auth_headers)
        assert response.status_code == 200, f"Failed to check deletability: {response.text}"
        
        data = response.json()
        # Item should be deletable since it has no orders
        assert data.get('can_delete') == True
        print("✅ Can-delete check works for item without orders")
    
    def test_check_menu_item_deletable_with_orders(self, auth_headers):
        """Test can-delete check for item that has orders"""
        # Get menu items - find one that's likely used in orders
        items_resp = requests.get(f"{BASE_URL}/api/restaurant/menu-items", headers=auth_headers)
        items = items_resp.json()
        
        # Get orders to find items that are used
        orders_resp = requests.get(f"{BASE_URL}/api/restaurant/orders", headers=auth_headers)
        orders = orders_resp.json()
        
        used_item_ids = set()
        for order in orders:
            for item in order.get('items', []):
                used_item_ids.add(item.get('menu_item_id'))
        
        if not used_item_ids:
            pytest.skip("No orders with menu items found")
        
        # Check one of the used items
        used_item_id = list(used_item_ids)[0]
        response = requests.get(f"{BASE_URL}/api/restaurant/menu-items/{used_item_id}/can-delete", headers=auth_headers)
        assert response.status_code == 200, f"Failed to check deletability: {response.text}"
        
        data = response.json()
        # Item should NOT be deletable since it has orders
        assert data.get('can_delete') == False
        assert "orders" in data.get('reason', '').lower()
        print(f"✅ Can-delete correctly blocks item with orders: {data.get('reason')}")
    
    def test_delete_menu_item_success(self, auth_headers):
        """Test deleting a menu item that has no orders"""
        # Get menu items
        items_resp = requests.get(f"{BASE_URL}/api/restaurant/menu-items", headers=auth_headers)
        items = items_resp.json()
        
        # Find our test item
        test_item = next((i for i in items if 'TEST_MenuItem' in i['name']), None)
        
        if not test_item:
            pytest.skip("Test menu item not found")
        
        item_id = test_item['id']
        
        # Delete the item
        response = requests.delete(f"{BASE_URL}/api/restaurant/menu-items/{item_id}", headers=auth_headers)
        assert response.status_code == 200, f"Failed to delete menu item: {response.text}"
        print("✅ Menu item deleted successfully")


class TestRoomChangeDuringCheckin:
    """Test room change feature during check-in"""
    
    def test_checkin_with_room_change(self, auth_headers):
        """Test checking in a guest with a different room"""
        # First get available rooms
        rooms_resp = requests.get(f"{BASE_URL}/api/rooms", headers=auth_headers)
        rooms = rooms_resp.json()
        available_rooms = [r for r in rooms if r.get('status') == 'Available']
        
        if len(available_rooms) < 2:
            pytest.skip("Need at least 2 available rooms for room change test")
        
        original_room = available_rooms[0]['room_number']
        new_room = available_rooms[1]['room_number']
        
        # Create a booking for original room
        booking_data = {
            "guest_name": "TEST_RoomChangeGuest",
            "guest_email": "roomchange@test.com",
            "guest_phone": "+94777111222",
            "room_number": original_room,
            "check_in_date": "2026-01-15",  # Today's date or past for immediate checkin
            "check_out_date": "2026-01-17",
            "stay_type": "Night Stay",
            "booking_amount": 10000
        }
        
        booking_resp = requests.post(f"{BASE_URL}/api/bookings", json=booking_data, headers=auth_headers)
        assert booking_resp.status_code == 200, f"Failed to create booking: {booking_resp.text}"
        booking = booking_resp.json()
        booking_id = booking.get('id')
        print(f"✅ Created booking {booking_id} for room {original_room}")
        
        # Check in with room change
        checkin_data = {
            "booking_id": booking_id,
            "advance_amount": 5000,
            "payment_method": "Cash",
            "notes": "Room change test",
            "new_room_number": new_room
        }
        
        checkin_resp = requests.post(f"{BASE_URL}/api/checkin", json=checkin_data, headers=auth_headers)
        assert checkin_resp.status_code == 200, f"Check-in with room change failed: {checkin_resp.text}"
        
        checkin_result = checkin_resp.json()
        # Check for either 'success' key or 'message' key indicating success
        assert checkin_result.get('message') is not None or checkin_result.get('customer') is not None
        print(f"✅ Check-in successful with room changed from {original_room} to {new_room}")
        
        # Verify the booking was updated with new room
        updated_booking_resp = requests.get(f"{BASE_URL}/api/bookings", headers=auth_headers)
        bookings = updated_booking_resp.json().get('bookings', [])
        updated_booking = next((b for b in bookings if b.get('id') == booking_id), None)
        
        if updated_booking:
            assert updated_booking.get('room_number') == new_room, "Booking should have new room"
            print(f"✅ Booking room updated to {new_room}")
        
        # Verify room status changed
        rooms_after = requests.get(f"{BASE_URL}/api/rooms", headers=auth_headers).json()
        new_room_status = next((r for r in rooms_after if r['room_number'] == new_room), None)
        if new_room_status:
            assert new_room_status.get('status') == 'Occupied', "New room should be occupied"
            print(f"✅ New room {new_room} is now occupied")


class TestGuestProofManagement:
    """Test upload and delete proof endpoints"""
    
    def test_upload_proof_for_guest(self, auth_headers):
        """Test uploading ID proof for an existing guest"""
        # Create a small test PDF
        dummy_pdf = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Count 0 /Kids [] >>\nendobj\nxref\n0 3\n0000000000 65535 f \n0000000009 00000 n \n0000000052 00000 n \ntrailer\n<< /Root 1 0 R /Size 3 >>\nstartxref\n101\n%%EOF"
        dummy_pdf_base64 = base64.b64encode(dummy_pdf).decode('utf-8')
        
        # Upload proof for existing guest by email
        upload_data = {
            "guest_id": "pdftest@example.com",  # Use email as identifier
            "id_proof": dummy_pdf_base64,
            "id_proof_filename": "uploaded_proof.pdf"
        }
        
        response = requests.post(f"{BASE_URL}/api/guests/upload-proof", json=upload_data, headers=auth_headers)
        
        if response.status_code == 404:
            pytest.skip("Guest not found for proof upload test")
        
        assert response.status_code == 200, f"Upload proof failed: {response.text}"
        data = response.json()
        assert data.get('bookings_updated', 0) > 0
        print(f"✅ Proof uploaded successfully, updated {data.get('bookings_updated')} bookings")
    
    def test_delete_proof_for_guest(self, auth_headers):
        """Test deleting ID proof for a guest"""
        response = requests.delete(f"{BASE_URL}/api/guests/delete-proof/pdftest@example.com", headers=auth_headers)
        
        if response.status_code == 404:
            pytest.skip("Guest not found for proof delete test")
        
        assert response.status_code == 200, f"Delete proof failed: {response.text}"
        data = response.json()
        print(f"✅ Proof deleted successfully, updated {data.get('bookings_updated')} bookings")


class TestCleanup:
    """Cleanup test data after tests"""
    
    def test_cleanup_test_data(self, auth_headers):
        """Clean up test bookings and data"""
        # Get all bookings
        bookings_resp = requests.get(f"{BASE_URL}/api/bookings", headers=auth_headers)
        bookings = bookings_resp.json().get('bookings', [])
        
        # Cancel test bookings
        test_bookings = [b for b in bookings if b.get('guest_name', '').startswith('TEST_')]
        for booking in test_bookings:
            try:
                requests.post(f"{BASE_URL}/api/cancel/{booking['id']}", headers=auth_headers)
                print(f"  Cancelled test booking: {booking.get('guest_name')}")
            except Exception:
                pass
        
        print(f"✅ Cleaned up {len(test_bookings)} test bookings")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
