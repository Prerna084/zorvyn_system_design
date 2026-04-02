# Finance dashboard backend

Backend for a finance dashboard with **role-based access control**, **financial record CRUD**, **aggregated dashboard metrics**, **JWT authentication**, and **PostgreSQL** persistence.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
set PYTHONPATH=.
python scripts/seed.py
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Interactive API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (Swagger UI)
- Health: `GET /health`

### Configuration

Optional `.env` (see values in `app/config.py`):

- `SECRET_KEY` — JWT signing secret (set a strong value outside local dev)
- `DATABASE_URL` — default `postgresql://postgres:postgres@localhost:5432/finance_db`

### Demo users (after seed)

| Email | Password | Role |
|--------|----------|------|
| admin@example.com | admin12345 | admin |
| analyst@example.com | analyst12345 | analyst |
| viewer@example.com | viewer12345 | viewer |

### Tests

```bash
pip install -r requirements-dev.txt
set PYTHONPATH=.
pytest tests -q
```

## Role model and access control

| Capability | viewer | analyst | admin |
|------------|--------|---------|-------|
| `GET /api/dashboard/summary` | no | yes | yes |
| `GET /api/records`, `GET /api/records/{id}` | yes | yes | yes |
| `POST/PATCH/DELETE /api/records` | no | no | yes |
| `GET/POST/PATCH /api/users`, deactivate user | no | no | yes |
| `GET /api/users/{id}` | own id only | own id only | any |
| `GET /api/auth/me`, `POST /api/auth/token` | yes | yes | yes |

- **Viewer**: Read-only access to raw financial records. Cannot view high-level dashboard summaries.
- **Analyst**: Full dashboard insights via summaries and raw record listing. No mutation rights.
- **Admin**: Full record and user management; soft-deletes financial records.

## API overview

All authenticated routes expect `Authorization: Bearer <token>`. Obtain a token with **OAuth2 password flow**:

`POST /api/auth/token`  
Form fields: `username` = email, `password` = password.

### Users (`/api/users`)

- `GET /api/users` — list (admin), pagination `skip`, `limit`
- `POST /api/users` — create (admin)
- `GET /api/users/{id}` — self or admin
- `PATCH /api/users/{id}` — update (admin)
- `DELETE /api/users/{id}` — set inactive (admin; cannot deactivate self)

### Financial records (`/api/records`)

- `GET /api/records` — filters: `type` (income|expense), `category`, `date_from`, `date_to`, `q` (search category/notes), `skip`, `limit`
- `POST /api/records` — body: `amount` (>0), `type`, `category`, `entry_date`, optional `notes`
- `PATCH /api/records/{id}` — partial update
- `DELETE /api/records/{id}` — soft delete

### Dashboard (`/api/dashboard`)

- `GET /api/dashboard/summary` — optional `date_from`, `date_to`, `recent_limit`  
  Returns: total income/expense, net balance, category totals, recent activity, weekly and monthly trend buckets.

## Data model

- **User**: email (unique), hashed password (bcrypt), `role`, `is_active`, timestamps.
- **FinancialRecord**: `amount`, `type` (income/expense), `category`, `entry_date`, `notes`, `created_by_id`, `deleted_at` for soft delete.

## Assumptions and tradeoffs

- **Single-tenant**: one shared ledger; no per-tenant isolation (can be added with `org_id` if needed).
- **PostgreSQL** for robustness and data integrity.
- **JWT** stateless auth; no refresh-token flow (acceptable for the assignment scope).
- **Validation**: Pydantic models + FastAPI; `422` returns structured `detail` for invalid input.
- **Soft delete** on records preserves history for analytics; adjust queries if hard delete is required.

## Project layout

```
app/
  main.py              # FastAPI app, router mount, validation error handler
  config.py
  database.py
  models.py
  core/security.py     # bcrypt + JWT
  api/deps.py          # auth + role dependencies
  api/routes/          # auth, users, records, dashboard
  schemas/             # Pydantic DTOs
  services/dashboard.py
scripts/seed.py
tests/test_smoke.py
```
