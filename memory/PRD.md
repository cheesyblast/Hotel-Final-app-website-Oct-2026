# Hotel Management System - PRD

## Original Problem Statement
Full-stack hotel management system with FastAPI backend + React frontend + MongoDB. Features include booking management, restaurant POS, stock management, payroll, income/expense tracking, calendar view, role-based access, and channel management.

## Architecture
- **Backend**: FastAPI (single server.py ~8.1k lines)
- **Frontend**: React (single App.js ~14.9k lines)
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
- Role-based access control (RBAC) with page-level permissions
- Settings page with channel management

### Session 1 Changes (Feb 2026)
1-18: Booking channel auto-rate, advance payments, dynamic categories, PDF uploads, guest details fixes, menu item actions, mobile nav, room changes, payroll fix, dark theme fixes, etc.

### Session 2 Changes (Apr 2026) - Financial Enhancement
19-27: Vendor management, "Add to Account" payment, mark expense as paid, enhanced daily/monthly sales reports with receivables/payables, modern dashboard with charts, Excel downloads.

### Session 3 Changes (Apr 2026) - Permissions & Cleanup
28. **Permission Bug Fix**: Login API now returns page_permissions. Navigation filters links via hasPageAccess(). All routes wrapped with PageGuard component that shows "Access Denied" for unauthorized pages. Admin always has full access.
29. **Reports Page Removed**: Route, component, and nav links all removed. All financial data available in Inc & Exp page.
30. **PDF Downloads Removed**: Only Excel downloads remain on Daily/Monthly Sales tabs.
31. **Enhanced Daily Sales Excel**: Individual record details under each section (CASH RECEIVED lists Room number, guest name, amount; same for BANK RECEIVED, CASH PAID, BANK PAID, PENDING RECEIVABLES, PENDING PAYABLES).
32. **Dead Code Cleanup**: Removed unused Reports component (~750 lines) and jsPDF imports.

## Key API Endpoints
- POST /api/auth/login (returns page_permissions), GET /api/auth/me
- CRUD /api/bookings, GET /api/bookings/upcoming
- POST /api/checkin (with new_room_number support)
- CRUD /api/rooms, GET /api/guests
- CRUD /api/restaurant/menu-items, /api/restaurant/orders
- CRUD /api/stock-items, /api/payroll/employees
- GET/POST /api/categories/{type}
- GET /api/daily-financial-summary (includes pending_receivables, pending_payables)
- GET /api/financial-reports/daily?date=YYYY-MM-DD
- GET /api/financial-reports/monthly?year=YYYY&month=MM (day-by-day breakdown)
- GET /api/vendors?search=xxx, POST /api/vendors
- PUT /api/expenses/{id}/mark-paid
- GET /api/users/available-pages (13 pages, no 'reports')
- CRUD /api/users (with page_permissions)

## Credentials
- Admin: admin / admin123

## Pending/Upcoming Tasks
- P1: Channel Manager real-time sync (placeholder currently)
- P2: Guest feedback system
- P2: Notification logs viewer
- P2: Guest checkout receipt PDF
- P3: Refactor monolithic App.js (~14.9k lines) and server.py (~8.1k lines)
