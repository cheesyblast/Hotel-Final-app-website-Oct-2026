# Hotel Management System - PRD

## Original Problem Statement
Full-stack hotel management system with FastAPI backend + React frontend + MongoDB. Features include booking management, restaurant POS, stock management, payroll, income/expense tracking, calendar view, role-based access, and channel management.

## Architecture
- **Backend**: FastAPI (single server.py ~7900 lines)
- **Frontend**: React (single App.js ~15400 lines)
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

### Latest Session Changes (Feb 2026)
1. **Booking Channel Auto-Rate**: Toggle per channel for auto commission calculation (ON by default)
2. **Removed "Made with" badge**: Hidden from index.html
3. **Default Dates**: All income/expense forms default to current date
4. **Restaurant Payment Modal**: Dark theme, item breakdown, order actions (View/Pay/Cancel), Room Bill status
5. **Advance Payment Routing**: Booking advances → Room Bookings Income (daily_sales)
6. **Advance Payment in Bookings**: Amount + payment method fields in booking form
7. **Polished Booking Popup**: 2-column dark layout, ID/Passport + Country same row, Stay Type + Channel same row, auto checkout date
8. **Dynamic Categories**: Empty by default, admin can add expense/income categories
9. **Payroll Fix**: Employee creation fixed (date serialization for MongoDB)
10. **PDF Upload**: Passport/ID proof upload in booking form, stored in guest details
11. **Guest Details Fix**: View details works for all guests (composite ID lookup), shows proof with download/delete/upload
12. **Menu Item Actions**: Dropdown with Edit/Delete, syncs to stock management, blocks delete if in orders
13. **Mobile Nav Fix**: Expenses dropdown items visible on mobile/tablets
14. **Room Change at Check-in**: Available room selector in check-in modal
15. **Restaurant Order Fix**: Corrected field name mismatch in deduct_stock_for_order
16. **Dashboard Pagination**: Upcoming bookings show 10 per page with pagination
17. **Income Section Theme**: Fixed white background in Income Records to dark theme
18. **Check-in Modal**: Converted to dark theme with booking amount summary

## Key API Endpoints
- POST /api/auth/login, GET /api/auth/me
- CRUD /api/bookings, GET /api/bookings/upcoming
- POST /api/checkin (with new_room_number support)
- CRUD /api/rooms
- GET /api/guests, GET /api/guests/{guest_id}
- POST /api/guests/upload-proof, DELETE /api/guests/delete-proof/{guest_id}
- CRUD /api/restaurant/menu-items, PUT /api/restaurant/menu-items/{id}
- GET /api/restaurant/menu-items/{id}/can-delete
- CRUD /api/restaurant/orders, POST /api/restaurant/orders/{id}/cancel
- PUT /api/restaurant/orders/{id}/items
- GET /api/restaurant/orders/room/{room_number}
- CRUD /api/stock-items, POST /api/stock-transactions
- GET/POST /api/categories/{type} (dynamic categories)
- CRUD /api/payroll/employees
- CRUD /api/booking-channels
- GET /api/daily-sales, GET /api/expenses, GET /api/incomes

## Credentials
- Admin: admin / admin123

## Pending/Upcoming Tasks
- P1: Password security (OTP reset, forced change) - E2E testing
- P1: Stock-to-Menu integration completion
- P2: Enhanced Calendar booking details (room numbers per booking)
- P2: Channel Manager real-time sync (placeholder currently)
- P3: Refactor monolithic App.js and server.py
- P3: Financial data model consolidation
- P3: Notification logs viewer
- P3: Guest feedback system
