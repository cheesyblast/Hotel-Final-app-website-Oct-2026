# Hotel Management System - PRD

## Original Problem Statement
Full-stack hotel management system with FastAPI backend + React frontend + MongoDB. Features include booking management, restaurant POS, stock management, payroll, income/expense tracking, calendar view, role-based access, and channel management.

## Architecture
- **Backend**: FastAPI (single server.py ~8100+ lines)
- **Frontend**: React (single App.js ~15700+ lines)
- **Database**: MongoDB
- **Auth**: JWT-based with 8hr token expiry

## What's Been Implemented

### Core Features (Completed)
- Authentication with JWT + Axios interceptor
- Dashboard with statistics, upcoming bookings (paginated 10/page), checked-in guests
- Room management (CRUD, status tracking)
- Booking management with searchable country dropdown
- Guest management with ID proof upload/download/delete (PDF)
- Restaurant POS with menu, orders, payment processing
- Calendar view with room occupancy details
- Financial tracking (income/expense with dynamic categories)
- Stock management system
- Payroll with employee management
- Role-based access control (RBAC)
- Settings page with channel management
- Reports with PDF/Excel download

### Session 1 Changes (Feb 2026)
1. Booking Channel Auto-Rate: Toggle per channel for auto commission calculation
2. Removed "Made with" badge
3. Default Dates for income/expense forms
4. Restaurant Payment Modal: Dark theme, item breakdown, order actions
5. Advance Payment Routing: Booking advances to Room Bookings Income
6. Advance Payment in Bookings: Amount + payment method fields
7. Polished Booking Popup: 2-column dark layout, auto checkout date
8. Dynamic Categories: Empty by default, admin adds categories
9. Payroll Fix: Employee creation (date serialization for MongoDB)
10. PDF Upload: Passport/ID proof upload in booking form
11. Guest Details Fix: View details works for all guests
12. Menu Item Actions: Dropdown with Edit/Delete, syncs to stock management
13. Mobile Nav Fix: Expenses dropdown items visible on mobile/tablets
14. Room Change at Check-in: Available room selector in check-in modal
15. Restaurant Order Fix: Corrected field name mismatch
16. Dashboard Pagination: Upcoming bookings show 10 per page
17. Income Section Theme: Fixed white background in Income Records
18. Check-in Modal: Converted to dark theme

### Session 2 Changes (Apr 2026) - Financial Enhancement
19. **Vendor Management**: Add/search vendors with autocomplete in expense form
20. **"Add to Account" Payment**: Expenses can be marked as pending payables (not paid at time of recording)
21. **Mark Expense as Paid**: Pending expenses can be settled later with chosen payment method
22. **Enhanced Daily Sales Report**: Shows Amounts Received (Cash/Bank), Amounts Paid, Pending Receivables (checked-in guests), Pending Payables (unpaid bills + commissions)
23. **Enhanced Monthly Sales Report**: Day-by-day ledger from 1st to last date with Rcvd Cash/Bank, Paid Cash/Bank, Pending, Net Balance columns + Grand Totals row
24. **Modern Inc & Exp Dashboard**: Tabbed interface (Overview, Daily Sales, Monthly Sales, Records) with Recharts bar/area charts showing daily growth and net profit trend
25. **6 Summary Cards**: Today's Received, Paid, Cash Balance, Bank Balance, Receivables, Payables
26. **Download Daily/Monthly Reports**: Excel (.xlsx) and PDF formats with detailed breakdowns
27. **Enhanced Expense Table**: Shows Vendor, Payment Status (Paid/Pending badge), Mark Paid action

## Key API Endpoints
- POST /api/auth/login, GET /api/auth/me
- CRUD /api/bookings, GET /api/bookings/upcoming
- POST /api/checkin (with new_room_number support)
- CRUD /api/rooms
- GET /api/guests, GET /api/guests/{guest_id}
- POST /api/guests/upload-proof, DELETE /api/guests/delete-proof/{guest_id}
- CRUD /api/restaurant/menu-items
- GET /api/restaurant/menu-items/{id}/can-delete
- CRUD /api/restaurant/orders
- CRUD /api/stock-items, POST /api/stock-transactions
- GET/POST /api/categories/{type} (dynamic categories)
- CRUD /api/payroll/employees
- CRUD /api/booking-channels
- GET /api/daily-sales
- GET /api/financial-summary
- GET /api/daily-financial-summary (includes pending_receivables, pending_payables)
- GET /api/financial-reports/daily?date=YYYY-MM-DD (enhanced with receivables/payables)
- GET /api/financial-reports/monthly?year=YYYY&month=MM (day-by-day breakdown + grand_totals)
- GET /api/vendors?search=xxx, POST /api/vendors
- PUT /api/expenses/{id}/mark-paid
- GET /api/expenses (includes vendor, payment_status fields)

## Key DB Schema
- Expense: `{ ..., vendor: str, payment_status: "Paid"|"Pending" }`
- DailySale: `{ ..., sale_type: str }`
- Vendor: `{ id, name, created_at }`
- Dynamic Category: `{ id, type: "expense"|"income", name }`

## Credentials
- Admin: admin / admin123

## Pending/Upcoming Tasks
- P1: Channel Manager real-time sync (placeholder currently)
- P2: Guest feedback system
- P2: Notification logs viewer
- P2: Guest checkout receipt PDF
- P3: Refactor monolithic App.js (~15.7k lines) and server.py (~8.1k lines)
- P3: Financial data model consolidation
