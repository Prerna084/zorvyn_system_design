<div align="center">
  <h1>🚀 Finance Dashboard API</h1>
  <p><b>A production-grade, highly scalable financial data engine.</b></p>
  
  [![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python&logoColor=white)](#)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.103+-009688.svg?logo=fastapi&logoColor=white)](#)
  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg?logo=postgresql&logoColor=white)](#)
  [![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg?logo=sqlalchemy&logoColor=white)](#)
  [![JWT](https://img.shields.io/badge/Security-JWT_OAuth2-black.svg?logo=jsonwebtokens&logoColor=white)](#)
</div>

<br/>

## 📸 API Preview

| Authentication | Users | Dashboard |
|---------------|------|-----------|
| ![](./assets/auth.png) | ![](./assets/users.png) | ![](./assets/dashboard.png) |

---

## 1. Overview

The **Finance Dashboard API** is a production-grade backend system designed to manage and analyze financial records for individuals or organizations. It provides secure, role-based access to financial data along with powerful aggregation capabilities for analytics such as income vs. expense tracking, category breakdowns, and time-based trends.

Built using **FastAPI** and **PostgreSQL**, the system follows a clean, scalable architecture with strong emphasis on security, performance, and maintainability.

---

## 🚀 Why This Project Matters

This project goes beyond basic CRUD operations and demonstrates:

- Secure authentication using JWT (OAuth2 flow)
- Role-based access control (RBAC)
- Scalable backend architecture (Controller → Service → Model)
- Real-world financial data aggregation (dashboard analytics)
- Optimized querying with filtering and pagination

It reflects how production backend systems are designed in real-world applications.

---

## 2. Tech Stack

* **Backend Framework:** FastAPI
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy
* **Validation:** Pydantic
* **Authentication:** JWT (OAuth2 Password Flow)
* **Rate Limiting:** slowapi
* **Server:** Uvicorn

---

## 3. Architecture

The project follows a structured **Controller → Service → Model** architecture to ensure separation of concerns and maintainability.

```
API → Controller → Service → Model → Database
```

### Project Structure

```
src/
├── config/          # Configuration and environment setup
├── controllers/     # Request handlers (Controller layer)
├── middlewares/     # Custom dependencies and middleware
├── models/          # SQLAlchemy models
├── routes/          # API route definitions
├── services/        # Business logic
├── validations/     # Pydantic schemas
└── main.py          # Application entry point
```

---

## 4. Role-Based Access Control (RBAC)

The API enforces strict role-based permissions:

| Capability          | Viewer | Analyst | Admin |
| ------------------- | ------ | ------- | ----- |
| View Records        | ✅      | ✅       | ✅     |
| Dashboard Analytics | ❌      | ✅       | ✅     |
| Modify Records      | ❌      | ❌       | ✅     |
| User Management     | ❌      | ❌       | ✅     |

### Roles

* **Viewer:** Read-only access to financial records
* **Analyst:** Access to analytics and insights
* **Admin:** Full control over records and users

---

## 5. API Endpoints

All endpoints require authentication:

```
Authorization: Bearer <token>
```

### Authentication (`/api/auth`)

### 📸 Authentication (JWT Login)

The API uses OAuth2 Password Flow for secure authentication.

- Generate token via `/api/auth/token`
- Use token in `Authorization: Bearer <token>`
- Required for all protected endpoints

![Authentication](./assets/auth.png)

---

### Users (`/api/users`)

### 📸 Get Users (Admin Only)

Returns a paginated list of users with role-based access.

- Requires JWT authentication  
- Supports pagination (`skip`, `limit`)  
- Admin-only endpoint  

![Users API](./assets/users.png)

* `GET /api/users` — List users (Admin)
* `POST /api/users` — Create user (Admin)
* `GET /api/users/{id}` — Get user (Admin or self)
* `PATCH /api/users/{id}` — Update user (Admin)
* `DELETE /api/users/{id}` — Deactivate user

---

### Financial Records (`/api/records`)

* `GET /api/records` — Fetch records (with filters & pagination)
* `POST /api/records` — Create record (Admin)
* `PATCH /api/records/{id}` — Update record (Admin)
* `DELETE /api/records/{id}` — Soft delete record (Admin)

#### Supported Filters

* `type` (income/expense)
* `category`
* `date_from`, `date_to`
* `q` (search query)
* `skip`, `limit` (pagination)

---

### Dashboard (`/api/dashboard`)

### 📸 Dashboard Analytics

Provides real-time aggregated financial insights including income, expenses, net balance, and category-wise breakdown.

- Single API call for complete analytics  
- Optimized aggregation queries  
- Role-based access (Analyst/Admin)  

![Dashboard](./assets/dashboard.png)

* `GET /api/dashboard/summary` — Aggregated financial insights

#### Sample Response

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

## 6. Key Design Decisions

* **Layered Architecture:**
  Business logic is isolated in services, keeping controllers lightweight and testable.

* **RBAC via Dependency Injection:**
  Custom dependencies enforce permissions before request execution.

* **Soft Deletes:**
  Records are not permanently removed; `deleted_at` ensures data integrity and auditability.

* **Advanced Filtering & Pagination:**
  Efficient querying for large datasets with flexible filters.

* **Single-Payload Dashboard:**
  Aggregations are computed in a single pass to reduce multiple API calls and improve performance.

---

## 7. Security & Production Considerations

* **JWT Authentication** for stateless security
* **Rate Limiting** (`5 requests/minute`) on login endpoint to prevent brute-force attacks
* **Data Isolation** enforced per user role
* **Input Validation** using Pydantic schemas

---

## 8. Environment Setup

Create a `.env` file in the root directory:

```
DATABASE_URL=postgresql://user:password@localhost:5432/finance_db
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 9. Installation & Running

### Step 1: Setup Environment

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### Step 2: Seed Database

```bash
set PYTHONPATH=.
python scripts/seed.py
```

### Step 3: Run Server

```bash
uvicorn src.main:app --reload
```

---

## 10. Demo Credentials

| Role    | Username            | Password       |
| ------- | ------------------- | -------------- |
| Admin   | admin@example.com   | admin12345     |
| Analyst | analyst@example.com | analyst12345   |
| Viewer  | viewer@example.com  | viewer12345    |

---

## 11. API Documentation

Interactive Swagger UI available at:

```
http://127.0.0.1:8000/docs
```

---

## 12. Testing

APIs can be tested using:

* Swagger UI
* Postman or any API client

---

## 13. Future Improvements

* Add caching (e.g., Redis) for dashboard queries
* Implement audit logging for sensitive operations
* Introduce automated test coverage
* Dockerize the application for easier deployment

---

## 14. Summary

This project demonstrates:

* Scalable backend architecture
* Secure authentication and authorization
* Efficient data handling and aggregation
* Production-ready design principles
