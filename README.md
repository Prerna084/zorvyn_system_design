# Finance Dashboard API

## 1. Project Overview

The Finance Dashboard API is a highly structured backend system designed with production-level architecture principles for managing and visualizing personal or enterprise financial records. Built with **FastAPI** and **PostgreSQL**, this backend enforces strict role-based data isolation while aggregating complex analytics (income vs. expense, monthly buckets, category-level totals) efficiently. Key features include JWT stateless authentication, data validation via Pydantic, advanced filtering, and a robust layered architecture.

---

## 2. Architecture

The codebase adheres strictly to an industry-standard **Controller-Service-Model** pattern. Dependency injection connects these layers ensuring clean, testable code.

```text
API → Service → Model → DB
```
### Project Layout
```
app/
├── api/             # Controllers (Route endpoints that handle HTTP exclusively)
├── services/        # Service Layer (Business logic and SQLAlchemy database queries)
├── models/          # Database Models (SQLAlchemy table definitions)
├── schemas/         # Pydantic Schemas (Input validation and response serializers)
├── core/            # Configuration and Core Security (JWT, settings)
├── dependencies/    # FastAPI Dependencies (Auth workflows and role enforcement)
└── main.py          # FastAPI application factory
```

---

## 3. Role-Based Access

The application features three distinct user tiers that are strictly enforced via FastAPI endpoint dependencies:

| Capability | Viewer | Analyst | Admin |
|------------|--------|---------|-------|
| `GET /api/dashboard/summary` | ❌ No | ✅ Yes | ✅ Yes |
| `GET /api/records` | ✅ Yes | ✅ Yes | ✅ Yes |
| `POST/PATCH/DELETE /api/records`| ❌ No | ❌ No | ✅ Yes |
| `Users Management` | ❌ No | ❌ No | ✅ Yes |

- **Viewer**: Baseline read-only access to raw financial records. Cannot view high-level dashboard summaries or metrics.
- **Analyst**: Deep analytics access. Granted permission to hit heavy aggregation endpoints (Dashboard) as well as list raw records. No mutation rights.
- **Admin**: Full authority. Can create, edit, or soft-delete financial records, and manage onboarding or deactivating of user accounts.

---

## 4. API List

All authenticated routes require an `Authorization: Bearer <token>` header.

### Authentication (`/api/auth`)
- `POST /api/auth/token` — OAuth2 Password Flow. Accepts `username` and `password` and returns a JWT token.
- `GET /api/auth/me` — Returns the currently authenticated user's profile.

### Users (`/api/users`)
- `GET /api/users` — List active users (Admin only). Includes `skip` and `limit` **pagination**.
- `POST /api/users` — Provision a new user (Admin only).
- `GET /api/users/{id}` — Retrieve details (Admin or self).
- `PATCH /api/users/{id}` — Update profile fields (Admin only).
- `DELETE /api/users/{id}` — Deactivate a user.

### Financial Records (`/api/records`)
- `GET /api/records` — Fetch financial records globally. Supports **Pagination** (`skip`, `limit`) and **Advanced Filtering** (`type`, `category`, `date_from`, `date_to`, `q`).
- `POST /api/records` — Create a new financial record. (Admin only)
- `PATCH /api/records/{id}` — Update record details. (Admin only)
- `DELETE /api/records/{id}` — **Soft delete** a record. (Admin only)

### Dashboard (`/api/dashboard`)
- `GET /api/dashboard/summary` — Analytics engine. Provides total net balance, income/expense breakdown, category groupings, and historic weekly/monthly buckets in a single payload.

**Sample Dashboard Response:**
```json
{
  "total_income": 8500.00,
  "total_expense": 3200.50,
  "net_balance": 5299.50,
  "category_totals": [
    { "category": "Food", "type": "expense", "amount": 450.00 }
  ],
  "recent_activity": [],
  "monthly_trends": []
}
```

---

## 5. Design Decisions

- **Layered Architecture (Service Layer):** Removed database query blocks from API routes to physically separate the `HTTP layer` from the `Persistence layer`. 
- **RBAC Dependency Injection:** Implemented modular `RequireAdmin` and `RequireAnyAuthenticated` dependency objects to instantly short-circuit unauthorized requests before hitting the controllers.
- **PostgreSQL Persistence:** Ejected SQLite in favor of a robust, fully relational DB.
- **Soft Deletes:** Deleting a `FinancialRecord` does not run a DROP against the table. Instead, `deleted_at` is stamped. Record fetching services filter heavily by `deleted_at IS NULL` to preserve historical integrity.
- **Advanced Filtering & Pagination:** Engineered robust `limit`/`offset` handling combined with multi-parameter filtering so frontend clients can safely browse massive datasets efficiently.
- **Single-Payload Dashboard:** Instead of requiring clients to send 5 different network requests for graph rendering, a custom Python dict/groupby generator iterates the data and returns all insights in one hyper-optimized loop.

---

## 6. How to Run

### Initial Setup
Ensure PostgreSQL is running locally on port 5432 with a database named `finance_db`.

```bash
# 1. Create your virtual environment and install dependencies
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt

# 2. Seed the PostgreSQL database with demo data + users
set PYTHONPATH=.                # CMD
$env:PYTHONPATH="."             # PowerShell
python scripts/seed.py
```

### Start Server
```bash
uvicorn app.main:app --reload
```

Test the API interactively at: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

## 7. Future Improvements

- Introduce caching for dashboard queries to handle heavy analytical loads.
- Add rate limiting for API endpoint protection.
- Implement audit logging for sensitive financial mutations or permission changes.
