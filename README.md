[![wakatime](https://wakatime.com/badge/user/cf5dfb0e-2b79-4a12-bcfd-ffd79a22a44f/project/2b4c39e6-27ea-4230-bcae-1a050ba2fbdf.svg)](https://wakatime.com/badge/user/cf5dfb0e-2b79-4a12-bcfd-ffd79a22a44f/project/2b4c39e6-27ea-4230-bcae-1a050ba2fbdf)


# TableTurn

**Restaurant Reservations, Orders & Kitchen Display System**

TableTurn is a backend system for managing restaurant reservations, table availability, food orders, kitchen operations, payments, and daily sales reporting.

The system is designed around the workflow of a real restaurant:

**Customer → Reservation → Table → Order → Kitchen → Payment → Report**

---

## 1. What is TableTurn?

TableTurn provides a centralized backend for restaurant operations.

Instead of managing reservations, orders, kitchen tickets, and payments separately, TableTurn connects these processes into one system.

### For diners

Diners can:

* Create an account
* Log in securely
* Check available tables
* Make reservations
* Cancel their own reservations

### For waiters

Waiters can:

* Manage customer seating
* Create orders
* Add items to orders
* Update order status where permitted
* Process payments
* View restaurant orders

### For kitchen staff

Kitchen staff can:

* View the kitchen order queue
* Receive new orders
* Track order preparation
* Update kitchen order status
* Receive live order updates through Server-Sent Events (SSE)

### For managers

Managers can:

* Create restaurant tables
* Manage menu items
* View daily turnover reports
* Access staff-level order information

### For the restaurant system

TableTurn also handles:

* Secure authentication
* Role-based authorization
* Reservation conflict prevention
* Redis caching
* Payment webhooks
* Webhook idempotency
* Firestore-powered kitchen events
* Rate limiting
* Request logging
* Background processing
* Database migrations

---

# 2. Main Features

## Authentication & Authorization

Users authenticate using email and password.

Passwords are securely hashed using **Argon2**, while authenticated requests use **JWT access tokens**.

The system has four roles:

| Role    | Purpose                                         |
| ------- | ----------------------------------------------- |
| Diner   | Makes and manages personal reservations         |
| Waiter  | Handles reservations, orders and payments       |
| Kitchen | Handles food preparation and kitchen operations |
| Manager | Manages tables, menu and reports                |

Access to protected endpoints is controlled using role-based authorization.

---

## Restaurant Tables

Managers can create restaurant tables with:

* Table code
* Capacity

Diners can check which tables are available for a particular party size and time range.

Table availability takes existing reservations into account.

---

## Reservations

The reservation system prevents overlapping bookings.

A reservation contains:

* Table
* Diner
* Party size
* Start time
* End time
* Status

Reservation statuses include:

* `confirmed`
* `seated`
* `cancelled`

The system uses the half-open time interval rule:

```text
[start, end)
```

This means a reservation ending at exactly the time another reservation starts does not conflict with the second reservation.

For example:

```text
Reservation A: 12:00 → 13:00
Reservation B: 13:00 → 14:00
```

These reservations can coexist.

---

# 3. Orders & Kitchen Operations

Waiters create orders for restaurant tables and add menu items to those orders.

Each order contains:

* Restaurant table
* Waiter
* Order status
* Total amount
* Ordered items
* Creation and update timestamps

Order statuses are:

```text
PLACED
   ↓
PREPARING
   ↓
READY
   ↓
SERVED
   ↓
PAID
```

The system validates status transitions so that orders cannot arbitrarily move between invalid states.

---

## Kitchen Display System

TableTurn includes a live Kitchen Display System (KDS).

When an order is created or its status changes, the kitchen can receive the update without manually refreshing the page.

Firestore stores the live kitchen queue data, while **Server-Sent Events (SSE)** provide the live stream to connected kitchen and waiter clients.

The intended flow is:

```text
Waiter
   │
   │ Create/Update Order
   ▼
FastAPI
   │
   ▼
Firestore
   │
   ▼
SSE Stream
   │
   ▼
Kitchen Display
```

This allows kitchen staff to see new tickets and status changes in near real time.

---

# 4. Payments

Waiters can create payment records for orders.

Payments contain:

* Order
* Amount
* Payment reference
* Payment method
* Status
* Timestamp

Payment statuses include:

```text
PENDING
SUCCESS
FAILED
```

The order amount is derived from the order's total amount.

---

## Payment Webhooks

TableTurn supports signed payment webhooks.

The webhook endpoint verifies the request using **HMAC-SHA512** and the configured secret.

The raw request body is used when generating the signature.

This protects the webhook endpoint against unauthorized requests.

### Idempotency

Webhook events are processed idempotently.

If the same payment event is received more than once, the system does not process the payment repeatedly.

For example:

```text
First webhook
    ↓
Payment marked successful
    ↓
Order marked PAID

Same webhook again
    ↓
Already processed
    ↓
No duplicate state change
```

---

# 5. Menu Management

The public menu can be viewed without authentication.

Managers can:

* Add menu items
* Update menu items
* Control menu availability

Menu responses are cached using **Redis** to reduce repeated database queries.

When a menu item is created or updated, the relevant cache is invalidated so users receive current menu information.

---

# 6. Daily Turnover Reports

Managers can request the restaurant's turnover for a specific date.

The report calculates the total value of successful payments recorded during that day.

Example:

```text
Date: 2026-09-25
Successful payments:
₦25,000
₦18,500
₦12,000

Total turnover:
₦55,500
```

---

# 7. API

The API is versioned under:

```text
/api/v1
```

### Authentication

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
```

### Tables

```text
POST /api/v1/tables
GET  /api/v1/tables/availability
```

### Reservations

```text
POST /api/v1/reservations
POST /api/v1/reservations/{id}/cancel
POST /api/v1/reservations/{id}/seat
```

### Orders

```text
POST /api/v1/orders
POST /api/v1/orders/{id}/items
GET  /api/v1/orders
POST /api/v1/orders/{id}/status
```

### Payments

```text
POST /api/v1/orders/{id}/payments
POST /api/v1/webhooks/payment
```

### Kitchen

```text
GET /api/v1/kitchen/queue
GET /api/v1/kitchen/stream
```

### Menu

```text
GET  /api/v1/menu
POST /api/v1/menu
PUT  /api/v1/menu/{id}
```

### Reports

```text
GET /api/v1/reports/turnover
```

---

# 8. Technology Stack

| Technology | Purpose                      |
| ---------- | ---------------------------- |
| Python     | Backend programming language |
| FastAPI    | REST API framework           |
| SQLModel   | Database models and ORM      |
| PostgreSQL | Primary relational database  |
| Alembic    | Database migrations          |
| JWT        | Authentication               |
| Argon2     | Password hashing             |
| Redis      | Menu caching                 |
| Firestore  | Live kitchen queue data      |
| SSE        | Real-time kitchen updates    |
| Docker     | Local infrastructure         |
| Pytest     | Automated testing            |
| SlowAPI    | Rate limiting                |

---

# 9. Project Structure

```text
tableturn/
│
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── deps.py
│   │   ├── firebase.py
│   │   ├── middleware.py
│   │   └── rate_limit.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   └── session.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── table.py
│   │   ├── reservation.py
│   │   ├── menu_item.py
│   │   ├── order.py
│   │   ├── order_item.py
│   │   ├── payment.py
│   │   └── processed_event.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── reservations.py
│   │   ├── tables.py
│   │   ├── menu.py
│   │   ├── orders.py
│   │   ├── payments.py
│   │   └── reports.py
│   │
│   ├── routes/
│   │   ├── auth.py
│   │   ├── tables.py
│   │   ├── reservations.py
│   │   ├── menu.py
│   │   ├── orders.py
│   │   ├── kitchen.py
│   │   ├── webhook.py
│   │   └── reports.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── reservation_service.py
│   │   ├── menu_service.py
│   │   ├── order_service.py
│   │   ├── kitchen_service.py
│   │   ├── payment_service.py
│   │   ├── webhook_service.py
│   │   ├── report_service.py
│   │   └── background_service.py
│   │
│   └── main.py
│
├── alembic/
├── tests/
├── docker-compose.yml
├── alembic.ini
├── pyproject.toml
├── .env
└── README.md
```

---

# 10. Application Architecture

TableTurn follows a layered backend architecture.

```text
Client
  │
  ▼
FastAPI Routes
  │
  ▼
Services
  │
  ▼
SQLModel / Database
  │
  ▼
PostgreSQL
```

Additional infrastructure supports specialized requirements:

```text
                 ┌─────────────┐
                 │   FastAPI   │
                 └──────┬──────┘
                        │
          ┌─────────────┼─────────────┐
          │             │             │
          ▼             ▼             ▼
     PostgreSQL       Redis       Firestore
      Main DB         Cache        KDS Data
                                      │
                                      ▼
                                     SSE
                                      │
                                      ▼
                                    Kitchen
```

### Why this separation?

Routes handle HTTP concerns.

Services contain business logic.

Models describe database data.

Schemas describe API input and output.

This keeps the application easier to test, maintain and extend.

---

# 11. Running the Project

## Requirements

You need:

* Python 3.14+
* Docker
* Docker Compose
* Git
* `uv`

---

## Clone the repository

```bash
git clone <repository-url>
cd TABLETURN-Restaurant-Reservations-Kitchen-Orders
```

---

## Install dependencies

```bash
uv sync
```

---

## Configure environment variables

Create a `.env` file:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/tableturn
SECRET_KEY=change-this-in-development
```

Additional Firebase configuration is required for the live kitchen stream.

The Firebase service account file should **never be committed to Git**.

---

## Start infrastructure

```bash
docker compose up -d
```

This starts the required infrastructure such as:

* PostgreSQL
* Redis

---

## Run database migrations

```bash
uv run alembic upgrade head
```

---

## Start the API

```bash
uv run fastapi dev app/main.py
```

The API will normally be available at:

```text
http://127.0.0.1:8000
```

---

# 12. API Documentation

FastAPI automatically provides interactive API documentation.

### Swagger UI

```text
/api/docs
```

Example:

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
/redoc
```

Example:

```text
http://127.0.0.1:8000/redoc
```

Swagger can be used to register users, authenticate, obtain a JWT token and test protected endpoints.

---

# 13. Database Migrations

Alembic manages database schema changes.

Create a migration after changing models:

```bash
uv run alembic revision --autogenerate -m "describe change"
```

Apply migrations:

```bash
uv run alembic upgrade head
```

Check the current migration:

```bash
uv run alembic current
```

---

# 14. Testing

TableTurn uses **pytest** for automated testing.

Run the complete test suite:

```bash
uv run pytest
```

Run with detailed output:

```bash
uv run pytest -v
```

The test suite covers important application behaviour including authentication, authorization, reservations, orders, payments, webhooks and other business rules.

---

# 15. Security

TableTurn includes several security mechanisms:

* Password hashing with Argon2
* JWT authentication
* Role-based authorization
* Signed payment webhooks
* HMAC-SHA512 signature verification
* Webhook idempotency
* Rate limiting
* Environment-based secrets
* Protected staff endpoints

Sensitive credentials and service-account files should never be committed to the repository.

---

# 16. Error Handling

The API uses standard HTTP status codes to communicate the result of requests.

Examples:

```text
201 Created
200 OK
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Unprocessable Entity
```

Examples of business conflicts include:

* Duplicate user registration
* Reservation overlap
* Invalid order status transition
* Duplicate payment processing
* Attempting to modify resources without the required role

---

# 17. Background Processing

TableTurn uses FastAPI background tasks for work that does not need to block the main request-response cycle.

For example, webhook processing can trigger background logging after the main payment operation has completed.

This keeps the primary API operation focused on the required business transaction.

---

# 18. Docker

Docker is used to provide consistent local infrastructure.

The project uses containers for services such as:

```text
PostgreSQL
Redis
```

Start services:

```bash
docker compose up -d
```

Stop services:

```bash
docker compose down
```

View running containers:

```bash
docker ps
```

---

# 19. Development Workflow

The project follows a feature-based Git workflow.

Typical workflow:

```text
Create feature branch
       ↓
Implement feature
       ↓
Run tests
       ↓
Review changes
       ↓
Commit
       ↓
Merge into main
```

Conventional Commit messages are used where possible:

```text
feat: add reservation seating
fix: prevent duplicate payment events
refactor: move authentication logic into service layer
test: add reservation conflict tests
```

---

# 20. Project Goals

TableTurn was built to demonstrate how a production-style restaurant backend can combine:

* REST APIs
* relational databases
* authentication
* authorization
* caching
* real-time communication
* payment processing
* webhook security
* automated testing
* containerized infrastructure
* database migrations
* background processing

The project focuses not only on exposing endpoints, but also on enforcing the business rules that make those endpoints reliable.

---

## 21. Status

TableTurn is a backend capstone project implementing the core restaurant workflow from reservation through order, kitchen preparation and payment.

Current development priorities include completing the automated test suite, CI/CD and final deployment/documentation verification.

---

## License

This project was created as a backend capstone project for educational and demonstration purposes.
