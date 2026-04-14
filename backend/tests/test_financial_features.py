"""
Test suite for Enhanced Hotel Management Financial System
Tests: Vendor management, Expense with 'Add to Account', Mark paid, Daily/Monthly reports, Categories
"""
import pytest
import requests
import os
from datetime import datetime, date

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuth:
    """Authentication tests"""
    
    def test_login_admin(self):
        """Test admin login with correct credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        assert data.get("user", {}).get("username") == "admin"
        return data["access_token"]
    
    def test_login_staff(self):
        """Test staff login with correct credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "staff1",
            "password": "staff123"
        })
        assert response.status_code == 200, f"Staff login failed: {response.text}"
        data = response.json()
        assert "access_token" in data


@pytest.fixture(scope="module")
def auth_token():
    """Get admin auth token for authenticated requests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture
def auth_headers(auth_token):
    """Headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestVendorManagement:
    """Vendor API tests"""
    
    def test_get_vendors_empty_search(self, auth_headers):
        """Test GET /api/vendors returns list"""
        response = requests.get(f"{BASE_URL}/api/vendors", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        assert isinstance(response.json(), list)
    
    def test_get_vendors_with_search(self, auth_headers):
        """Test GET /api/vendors?search=xxx filters vendors"""
        response = requests.get(f"{BASE_URL}/api/vendors?search=test", headers=auth_headers)
        assert response.status_code == 200
        # Should return list (may be empty if no matching vendors)
        assert isinstance(response.json(), list)
    
    def test_add_vendor(self, auth_headers):
        """Test POST /api/vendors adds new vendor"""
        vendor_name = f"TEST_Vendor_{datetime.now().strftime('%H%M%S')}"
        response = requests.post(f"{BASE_URL}/api/vendors", 
            json={"name": vendor_name}, headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("name") == vendor_name
        
        # Verify vendor appears in list
        list_response = requests.get(f"{BASE_URL}/api/vendors?search={vendor_name}", headers=auth_headers)
        assert vendor_name in list_response.json()
    
    def test_add_duplicate_vendor_fails(self, auth_headers):
        """Test adding duplicate vendor returns error"""
        vendor_name = f"TEST_DupVendor_{datetime.now().strftime('%H%M%S')}"
        # Add first time
        requests.post(f"{BASE_URL}/api/vendors", json={"name": vendor_name}, headers=auth_headers)
        # Add second time - should fail
        response = requests.post(f"{BASE_URL}/api/vendors", json={"name": vendor_name}, headers=auth_headers)
        assert response.status_code == 400


class TestDynamicCategories:
    """Dynamic expense/income categories tests"""
    
    def test_get_expense_categories(self, auth_headers):
        """Test GET /api/categories/expense returns list"""
        response = requests.get(f"{BASE_URL}/api/categories/expense", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_income_categories(self, auth_headers):
        """Test GET /api/categories/income returns list"""
        response = requests.get(f"{BASE_URL}/api/categories/income", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_add_expense_category(self, auth_headers):
        """Test POST /api/categories/expense adds new category"""
        cat_name = f"TEST_ExpCat_{datetime.now().strftime('%H%M%S')}"
        response = requests.post(f"{BASE_URL}/api/categories/expense", 
            json={"name": cat_name}, headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        
        # Verify category appears in list
        list_response = requests.get(f"{BASE_URL}/api/categories/expense", headers=auth_headers)
        assert cat_name in list_response.json()
    
    def test_add_income_category(self, auth_headers):
        """Test POST /api/categories/income adds new category"""
        cat_name = f"TEST_IncCat_{datetime.now().strftime('%H%M%S')}"
        response = requests.post(f"{BASE_URL}/api/categories/income", 
            json={"name": cat_name}, headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        
        # Verify category appears in list
        list_response = requests.get(f"{BASE_URL}/api/categories/income", headers=auth_headers)
        assert cat_name in list_response.json()


class TestExpenseManagement:
    """Expense CRUD and payment status tests"""
    
    def test_create_expense_cash_paid(self, auth_headers):
        """Test creating expense with Cash payment - should be Paid status"""
        today = date.today().isoformat()
        expense_data = {
            "description": "TEST_Cash_Expense",
            "amount": 1000,
            "category": "Maintenance",
            "payment_method": "Cash",
            "vendor": "",
            "expense_date": today
        }
        response = requests.post(f"{BASE_URL}/api/expenses", json=expense_data, headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("payment_status") == "Paid", f"Expected Paid, got {data.get('payment_status')}"
        assert data.get("amount") == 1000
        return data.get("id")
    
    def test_create_expense_add_to_account_pending(self, auth_headers):
        """Test creating expense with 'Add to Account' - should be Pending status"""
        today = date.today().isoformat()
        expense_data = {
            "description": "TEST_AddToAccount_Expense",
            "amount": 2500,
            "category": "Utilities",
            "payment_method": "Add to Account",
            "vendor": "TEST_Vendor_Pending",
            "expense_date": today
        }
        response = requests.post(f"{BASE_URL}/api/expenses", json=expense_data, headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("payment_status") == "Pending", f"Expected Pending, got {data.get('payment_status')}"
        assert data.get("vendor") == "TEST_Vendor_Pending"
        return data.get("id")
    
    def test_vendor_auto_saved_on_expense_creation(self, auth_headers):
        """Test that vendor is auto-saved when creating expense with new vendor"""
        vendor_name = f"TEST_AutoVendor_{datetime.now().strftime('%H%M%S')}"
        today = date.today().isoformat()
        expense_data = {
            "description": "TEST_AutoVendor_Expense",
            "amount": 500,
            "category": "Maintenance",
            "payment_method": "Cash",
            "vendor": vendor_name,
            "expense_date": today
        }
        response = requests.post(f"{BASE_URL}/api/expenses", json=expense_data, headers=auth_headers)
        assert response.status_code == 200
        
        # Verify vendor was auto-saved
        vendors_response = requests.get(f"{BASE_URL}/api/vendors?search={vendor_name}", headers=auth_headers)
        assert vendor_name in vendors_response.json(), "Vendor was not auto-saved"
    
    def test_mark_expense_as_paid(self, auth_headers):
        """Test PUT /api/expenses/{id}/mark-paid changes status to Paid"""
        # First create a pending expense
        today = date.today().isoformat()
        expense_data = {
            "description": "TEST_MarkPaid_Expense",
            "amount": 1500,
            "category": "Utilities",
            "payment_method": "Add to Account",
            "vendor": "TEST_MarkPaid_Vendor",
            "expense_date": today
        }
        create_response = requests.post(f"{BASE_URL}/api/expenses", json=expense_data, headers=auth_headers)
        assert create_response.status_code == 200
        expense_id = create_response.json().get("id")
        assert create_response.json().get("payment_status") == "Pending"
        
        # Mark as paid
        mark_paid_response = requests.put(
            f"{BASE_URL}/api/expenses/{expense_id}/mark-paid",
            json={"payment_method": "Cash"},
            headers=auth_headers
        )
        assert mark_paid_response.status_code == 200, f"Mark paid failed: {mark_paid_response.text}"
        
        # Verify status changed by fetching all expenses
        expenses_response = requests.get(f"{BASE_URL}/api/expenses", headers=auth_headers)
        expenses = expenses_response.json()
        updated_expense = next((e for e in expenses if e.get("id") == expense_id), None)
        assert updated_expense is not None, "Expense not found after mark paid"
        assert updated_expense.get("payment_status") == "Paid", f"Status not updated: {updated_expense.get('payment_status')}"
    
    def test_get_expenses_list(self, auth_headers):
        """Test GET /api/expenses returns list with payment_status field"""
        response = requests.get(f"{BASE_URL}/api/expenses", headers=auth_headers)
        assert response.status_code == 200
        expenses = response.json()
        assert isinstance(expenses, list)
        # Check that expenses have payment_status field
        if len(expenses) > 0:
            assert "payment_status" in expenses[0], "payment_status field missing"
    
    def test_delete_expense(self, auth_headers):
        """Test DELETE /api/expenses/{id}"""
        # Create expense to delete
        today = date.today().isoformat()
        expense_data = {
            "description": "TEST_Delete_Expense",
            "amount": 100,
            "category": "Maintenance",
            "payment_method": "Cash",
            "expense_date": today
        }
        create_response = requests.post(f"{BASE_URL}/api/expenses", json=expense_data, headers=auth_headers)
        expense_id = create_response.json().get("id")
        
        # Delete
        delete_response = requests.delete(f"{BASE_URL}/api/expenses/{expense_id}", headers=auth_headers)
        assert delete_response.status_code == 200


class TestIncomeManagement:
    """Income CRUD tests"""
    
    def test_create_income(self, auth_headers):
        """Test POST /api/incomes creates income record"""
        today = date.today().isoformat()
        income_data = {
            "description": "TEST_Income_Record",
            "amount": 5000,
            "category": "Restaurant",
            "payment_method": "Cash",
            "income_date": today,
            "guest_name": "Test Guest"
        }
        response = requests.post(f"{BASE_URL}/api/incomes", json=income_data, headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("amount") == 5000
        assert data.get("category") == "Restaurant"
        return data.get("id")
    
    def test_get_incomes_list(self, auth_headers):
        """Test GET /api/incomes returns list"""
        response = requests.get(f"{BASE_URL}/api/incomes", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_delete_income(self, auth_headers):
        """Test DELETE /api/incomes/{id}"""
        # Create income to delete
        today = date.today().isoformat()
        income_data = {
            "description": "TEST_Delete_Income",
            "amount": 200,
            "category": "Other",
            "payment_method": "Cash",
            "income_date": today
        }
        create_response = requests.post(f"{BASE_URL}/api/incomes", json=income_data, headers=auth_headers)
        income_id = create_response.json().get("id")
        
        # Delete
        delete_response = requests.delete(f"{BASE_URL}/api/incomes/{income_id}", headers=auth_headers)
        assert delete_response.status_code == 200


class TestDailyFinancialSummary:
    """Daily financial summary API tests"""
    
    def test_get_daily_financial_summary(self, auth_headers):
        """Test GET /api/daily-financial-summary returns receivables and payables"""
        response = requests.get(f"{BASE_URL}/api/daily-financial-summary", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Check required fields
        assert "total_revenue" in data
        assert "total_expenses" in data
        assert "cash_balance" in data
        assert "bank_balance" in data
        assert "pending_receivables" in data, "pending_receivables missing"
        assert "pending_payables" in data, "pending_payables missing"
        assert "date" in data


class TestDailyFinancialReport:
    """Enhanced daily financial report tests"""
    
    def test_get_daily_report_today(self, auth_headers):
        """Test GET /api/financial-reports/daily returns enhanced report"""
        today = date.today().isoformat()
        response = requests.get(f"{BASE_URL}/api/financial-reports/daily?date={today}", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Check structure
        assert "date" in data
        assert "received" in data
        assert "paid" in data
        assert "pending_receivables" in data
        assert "pending_payables" in data
        assert "net_position" in data
        
        # Check received structure
        received = data.get("received", {})
        assert "cash" in received
        assert "bank" in received
        assert "total" in received
        assert "details" in received
        
        # Check paid structure
        paid = data.get("paid", {})
        assert "cash" in paid
        assert "bank" in paid
        assert "total" in paid
        assert "details" in paid
        
        # Check pending structures
        assert "total" in data.get("pending_receivables", {})
        assert "total" in data.get("pending_payables", {})
    
    def test_daily_report_without_date_uses_today(self, auth_headers):
        """Test GET /api/financial-reports/daily without date param uses today"""
        response = requests.get(f"{BASE_URL}/api/financial-reports/daily", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data.get("date") == date.today().isoformat()


class TestMonthlyFinancialReport:
    """Enhanced monthly financial report with day-by-day breakdown tests"""
    
    def test_get_monthly_report_current_month(self, auth_headers):
        """Test GET /api/financial-reports/monthly returns day-by-day breakdown"""
        today = date.today()
        response = requests.get(
            f"{BASE_URL}/api/financial-reports/monthly?year={today.year}&month={today.month}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Check structure
        assert "month" in data
        assert "year" in data
        assert "month_number" in data
        assert "days_in_month" in data
        assert "daily_breakdown" in data
        assert "grand_totals" in data
        
        # Check daily_breakdown is list with correct number of days
        daily_breakdown = data.get("daily_breakdown", [])
        assert isinstance(daily_breakdown, list)
        assert len(daily_breakdown) == data.get("days_in_month"), \
            f"Expected {data.get('days_in_month')} days, got {len(daily_breakdown)}"
        
        # Check each day has required fields
        if len(daily_breakdown) > 0:
            day_entry = daily_breakdown[0]
            assert "date" in day_entry
            assert "day" in day_entry
            assert "received_cash" in day_entry
            assert "received_bank" in day_entry
            assert "total_received" in day_entry
            assert "paid_cash" in day_entry
            assert "paid_bank" in day_entry
            assert "total_paid" in day_entry
            assert "pending_payables" in day_entry
            assert "net_balance" in day_entry
        
        # Check grand_totals structure
        grand_totals = data.get("grand_totals", {})
        assert "received_cash" in grand_totals
        assert "received_bank" in grand_totals
        assert "total_received" in grand_totals
        assert "paid_cash" in grand_totals
        assert "paid_bank" in grand_totals
        assert "total_paid" in grand_totals
        assert "pending_payables" in grand_totals
        assert "net_balance" in grand_totals
    
    def test_monthly_report_without_params_uses_current_month(self, auth_headers):
        """Test GET /api/financial-reports/monthly without params uses current month"""
        response = requests.get(f"{BASE_URL}/api/financial-reports/monthly", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        today = date.today()
        assert data.get("year") == today.year
        assert data.get("month_number") == today.month
    
    def test_monthly_report_january(self, auth_headers):
        """Test monthly report for January has 31 days"""
        response = requests.get(
            f"{BASE_URL}/api/financial-reports/monthly?year=2026&month=1",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("days_in_month") == 31
        assert len(data.get("daily_breakdown", [])) == 31


class TestPayablesCalculation:
    """Test that pending payables are correctly calculated"""
    
    def test_pending_expense_appears_in_payables(self, auth_headers):
        """Test that 'Add to Account' expense appears in pending payables"""
        # Get initial payables
        initial_summary = requests.get(f"{BASE_URL}/api/daily-financial-summary", headers=auth_headers).json()
        initial_payables = initial_summary.get("pending_payables", 0)
        
        # Create pending expense
        today = date.today().isoformat()
        expense_data = {
            "description": "TEST_Payables_Check",
            "amount": 3000,
            "category": "Utilities",
            "payment_method": "Add to Account",
            "vendor": "TEST_Payables_Vendor",
            "expense_date": today
        }
        create_response = requests.post(f"{BASE_URL}/api/expenses", json=expense_data, headers=auth_headers)
        assert create_response.status_code == 200
        expense_id = create_response.json().get("id")
        
        # Check payables increased
        new_summary = requests.get(f"{BASE_URL}/api/daily-financial-summary", headers=auth_headers).json()
        new_payables = new_summary.get("pending_payables", 0)
        assert new_payables >= initial_payables + 3000, \
            f"Payables should have increased by 3000. Was {initial_payables}, now {new_payables}"
        
        # Mark as paid
        requests.put(f"{BASE_URL}/api/expenses/{expense_id}/mark-paid", 
            json={"payment_method": "Cash"}, headers=auth_headers)
        
        # Check payables decreased
        final_summary = requests.get(f"{BASE_URL}/api/daily-financial-summary", headers=auth_headers).json()
        final_payables = final_summary.get("pending_payables", 0)
        assert final_payables < new_payables, "Payables should decrease after marking paid"


class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_expenses(self, auth_headers):
        """Delete TEST_ prefixed expenses"""
        response = requests.get(f"{BASE_URL}/api/expenses", headers=auth_headers)
        if response.status_code == 200:
            expenses = response.json()
            for exp in expenses:
                if exp.get("description", "").startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/expenses/{exp.get('id')}", headers=auth_headers)
        assert True  # Cleanup always passes
    
    def test_cleanup_test_incomes(self, auth_headers):
        """Delete TEST_ prefixed incomes"""
        response = requests.get(f"{BASE_URL}/api/incomes", headers=auth_headers)
        if response.status_code == 200:
            incomes = response.json()
            for inc in incomes:
                if inc.get("description", "").startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/incomes/{inc.get('id')}", headers=auth_headers)
        assert True  # Cleanup always passes
