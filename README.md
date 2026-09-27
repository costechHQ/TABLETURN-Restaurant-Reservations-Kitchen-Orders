[![wakatime](https://wakatime.com/badge/user/cf5dfb0e-2b79-4a12-bcfd-ffd79a22a44f/project/2b4c39e6-27ea-4230-bcae-1a050ba2fbdf.svg)](https://wakatime.com/badge/user/cf5dfb0e-2b79-4a12-bcfd-ffd79a22a44f/project/2b4c39e6-27ea-4230-bcae-1a050ba2fbdf)

# TableTurn — Restaurant Reservations & Kitchen Orders

TableTurn is a restaurant management backend built with FastAPI, SQLModel, PostgreSQL, Redis, and Firebase Firestore.

It provides a complete workflow for restaurant reservations, waiter orders, kitchen operations, payments, and real-time kitchen updates.

The project was developed as a backend capstone project by **Team Swift Hunters — Lilian & Chris**.

---

## Table of Contents

* [Project Overview](#project-overview)
* [Problem Statement](#problem-statement)
* [Core Features](#core-features)
* [User Roles](#user-roles)
* [Technology Stack](#technology-stack)
* [Architecture](#architecture)
* [Database Design](#database-design)
* [Reservation Logic](#reservation-logic)
* [Kitchen Order Workflow](#kitchen-order-workflow)
* [Real-Time Kitchen Updates](#real-time-kitchen-updates)
* [Payments and Webhooks](#payments-and-webhooks)
* [Authentication and Authorization](#authentication-and-authorization)
* [Caching](#caching)
* [API Overview](#api-overview)
* [Testing](#testing)
* [Docker](#docker)
* [Environment Variables](#environment-variables)
* [Running the Project Locally](#running-the-project-locally)
* [Major Challenges and Solutions](#major-challenges-and-solutions)
* [Security Considerations](#security-considerations)
* [Project Status](#project-status)

---

## Project Overview

TableTurn is designed around the day-to-day workflow of a restaurant.

A diner should be able to find an available table and make a reservation without being double-booked.

A waiter should be able to seat diners and create orders.

The kitchen should immediately receive new orders and process them through a controlled workflow.

Managers should be able to manage restaurant tables, menu items, staff accounts, and view turnover information.

Online payments are handled through signed payment webhooks, while Firestore is used to provide real-time kitchen updates.

---

## Problem Statement

Restaurant systems have several problems that require more than basic CRUD operations:

1. Two diners must not be able to successfully reserve the same table for overlapping periods.
2. Reservations that only touch at their boundaries should be allowed.
3. Kitchen orders must follow a strict state transition.
4. New kitchen tickets should appear in real time.
5. Payment webhooks can be delivered more than once and must therefore be idempotent.
6. Different restaurant staff need different levels of access.
7. Frequently requested data should not unnecessarily hit the database.

TableTurn addresses these problems through database transactions, row locking, role-based authorization, state machines, Server-Sent Events, webhook signatures, idempotency records, Redis caching, and automated tests.

---

# Core Features

### Authentication

* User registration
* User login
* JWT authentication
* Password hashing with Argon2
* Role-based access control
* Manager-controlled staff account creation
* Public registration creates diner accounts only

### Reservations

* Table availability checking
* Reservation creation
* Reservation cancellation
* Reservation seating
* Party-size validation
* Past-time validation
* Exact reservation overlap detection
* PostgreSQL row locking for concurrent reservations

### Orders

* Waiters can create orders
* Waiters can add menu items
* Menu availability validation
* Automatic order total calculation
* Order item quantity and price tracking
* Order status management

### Kitchen

* Kitchen queue
* Kitchen order state machine
* NEW/PLACED → PREPARING → READY → SERVED
* Invalid state transitions rejected
* Real-time kitchen updates using SSE
* Firestore kitchen queue

### Payments

* Payment recording
* Payment status tracking
* Paystack webhook processing
* HMAC-SHA512 signature verification
* Webhook idempotency
* Automatic order payment status update

### Management

* Restaurant table management
* Menu management
* Staff account provisioning
* Turnover reports

### Infrastructure

* PostgreSQL
* Redis
* Firebase Firestore
* Docker Compose
* Alembic migrations
* Automated pytest test suite
* CI workflow

---

# User Roles

TableTurn has four main roles:

| Role    | Responsibility                                     |
| ------- | -------------------------------------------------- |
| DINER   | Makes and manages their reservations               |
| WAITER  | Seats diners, creates orders, and records payments |
| KITCHEN | Views kitchen queue and processes orders           |
| MANAGER | Manages staff, tables, menu, and reports           |

Role authorization is enforced through FastAPI dependencies.

For example, a kitchen endpoint cannot be accessed by a diner even when the diner has a valid JWT.

---

# Technology Stack

## Backend

* Python
* FastAPI
* SQLModel
* Pydantic
* JWT

## Database

* PostgreSQL
* Alembic

## Caching

* Redis

## Real-Time Data

* Firebase Firestore
* Server-Sent Events (SSE)

## Payments

* Paystack webhook integration

## Security

* Argon2 password hashing
* JWT authentication
* Role-based authorization
* HMAC-SHA512 webhook verification
* Rate limiting

## Development

* uv
* pytest
* Docker
* Docker Compose
* GitHub Actions

---

# Architecture

The project follows a layered FastAPI structure:

```text
tableturn/
│
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── deps.py
│   │   ├── firebase.py
│   │   ├── rate_limit.py
│   │   └── security.py
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
│   │
│   ├── routes/
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── reservation_service.py
│   │   ├── order_service.py
│   │   ├── kitchen_service.py
│   │   ├── payment_service.py
│   │   ├── webhook_service.py
│   │   ├── menu_service.py
│   │   ├── report_service.py
│   │   └── floor_feed_service.py
│   │
│   └── main.py
│
├── alembic/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

The routes handle HTTP requests and authorization, while services contain important business logic.

---

# Database Design

PostgreSQL is the primary source of truth for transactional restaurant data.

Main entities include:

### Users

```text
id
email
password_hash
role
created_at
```

Email addresses are unique.

### Restaurant Tables

```text
id
code
capacity
```

Table codes are unique.

### Reservations

```text
id
table_id
diner_id
party_size
start_at
end_at
status
```

An index is used on:

```text
(table_id, start_at, end_at)
```

### Menu Items

```text
id
name
description
price
is_available
```

### Orders

```text
id
table_id
waiter_id
status
total_amount
placed_at
updated_at
```

An index is used on:

```text
(status, placed_at)
```

### Order Items

```text
id
order_id
menu_item_id
qty
unit_price
total_amount
notes
status
```

`unit_price` records the price of the menu item at the time it was added to the order. This prevents historical orders from changing when the menu price changes later.

### Payments

```text
id
order_id
amount
method
recorded_by
recorded_at
status
reference
```

### Processed Events

```text
event_id
reference
processed_at
```

This table supports webhook idempotency.

---

# Reservation Logic

One of the most important parts of TableTurn is preventing overlapping reservations.

The system uses the standard half-open interval overlap rule:

```text
new.start < existing.end
AND
new.end > existing.start
```

For example:

```text
Existing: 19:00 — 21:00
New:      20:00 — 22:00
```

These overlap and the second reservation receives:

```text
409 Conflict
```

However:

```text
Existing: 19:00 — 21:00
New:      21:00 — 23:00
```

These reservations only touch at the boundary, so the second reservation is allowed.

The reservation service also checks:

* Table exists
* Party size does not exceed capacity
* Start time is not in the past
* End time is after start time
* Existing cancelled reservations do not block availability

## Concurrency Protection

A simple overlap query is not enough when two users attempt the same reservation at almost exactly the same time.

The reservation service locks the table row inside the transaction before checking for conflicting reservations.

This ensures that concurrent requests cannot both successfully reserve the same table and time slot.

The project includes a concurrency test verifying that two simultaneous attempts result in:

```text
Request 1 → 201 Created
Request 2 → 409 Conflict
```

---

# Kitchen Order Workflow

Kitchen orders use a strict state machine.

The allowed workflow is:

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

The kitchen-specific processing flow requires:

```text
PLACED → PREPARING
PREPARING → READY
READY → SERVED
```

Skipping a state is rejected.

For example:

```text
PLACED → READY
```

returns:

```text
409 Conflict
```

This prevents invalid kitchen states from entering the system.

---

# Real-Time Kitchen Updates

TableTurn uses Firebase Firestore together with Server-Sent Events.

When an order is created or its status changes, the system synchronizes the relevant information to the Firestore `kitchen_queue` collection.

The kitchen stream endpoint:

```text
GET /api/v1/kitchen/stream
```

keeps an HTTP connection open and sends events to connected kitchen clients.

Example event:

```text
data: {
    "type": "ADDED",
    "data": {
        "order_id": 123,
        "status": "NEW"
    }
}
```

SSE was chosen because the kitchen screen mainly needs server-to-client updates rather than a two-way communication channel.

---

# Floor Feed

Firestore also contains a `floor_feed` collection.

It records important restaurant timeline events such as:

* Reservation seated
* Reservation cancelled
* Order ready

This provides a timeline that can be consumed by a restaurant floor interface.

---

# Payments and Webhooks

Online payment completion is handled through a payment webhook.

The webhook endpoint is:

```text
POST /api/v1/webhooks/payment
```

The request is verified using the Paystack signature:

```text
x-paystack-signature
```

The signature is calculated using HMAC-SHA512 over the **raw request body**.

Invalid signatures are rejected with:

```text
401 Unauthorized
```

## Webhook Idempotency

Payment providers can send the same webhook event more than once.

TableTurn stores processed event IDs in the `processed_events` table.

The first event is processed normally.

If the same event arrives again, the system returns successfully without applying the payment state change again.

This prevents duplicate processing.

---

# Authentication and Authorization

Passwords are never stored in plain text.

TableTurn uses Argon2 password hashing.

Authentication uses JWT access tokens.

The token contains information required to identify the authenticated user and their role.

Protected routes use dependencies such as:

```text
get_current_user
require_role(...)
```

## Staff Account Provisioning

Public registration does not allow users to choose their own role.

A public registration automatically creates:

```text
DINER
```

Staff accounts are created through:

```text
POST /api/v1/auth/staff
```

and only managers can access this endpoint.

Allowed staff roles are:

```text
WAITER
KITCHEN
MANAGER
```

This prevents a user from registering themselves as a manager or kitchen administrator.

---

# Rate Limiting

Login is protected with a rate limit:

```text
5 requests per minute
```

This reduces the risk of repeated login attempts.

During automated testing, the limiter state is reset between tests so that one test does not affect another.

The production rate limit itself remains unchanged.

---

# Caching

Redis is used for caching frequently requested data.

The menu endpoint is cached because menu information can be requested frequently while changing less often than transactional data.

Cache invalidation is performed when menu data changes so stale menu information is not served indefinitely.

---

# API Overview

All API endpoints are grouped under:

```text
/api/v1
```

## Authentication

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/staff
```

## Tables

```text
GET  /api/v1/tables/availability
POST /api/v1/tables
```

## Reservations

```text
POST /api/v1/reservations
POST /api/v1/reservations/{id}/cancel
POST /api/v1/reservations/{id}/seat
```

## Orders

```text
POST /api/v1/orders
POST /api/v1/orders/{id}/items
POST /api/v1/orders/{id}/status
GET  /api/v1/orders
POST /api/v1/orders/{id}/payments
```

## Kitchen

```text
GET /api/v1/kitchen/queue
GET /api/v1/kitchen/stream
```

## Menu

```text
GET  /api/v1/menu
POST /api/v1/menu
PUT  /api/v1/menu/{id}
```

## Reports

```text
GET /api/v1/reports/turnover
```

## Payments

```text
POST /api/v1/webhooks/payment
```

Interactive API documentation is available through FastAPI's Swagger UI when the application is running.

---

# Testing

Automated tests are written using pytest.

The test suite covers:

* Authentication
* Role-based authorization
* Staff account provisioning
* Reservation creation
* Reservation overlap
* Boundary-touching reservations
* Reservation capacity
* Past reservation times
* Reservation cancellation
* Reservation seating
* Concurrent reservation attempts
* Order creation
* Kitchen queue
* Kitchen state transitions
* Invalid kitchen transitions
* SSE event streaming
* Payments
* Paystack webhook signatures
* Webhook idempotency
* Menu functionality
* Caching behavior
* Other API requirements

The complete test suite currently passes:

```text
36 passed
```

Run all tests with:

```bash
uv run pytest -q
```

Run authentication tests only:

```bash
uv run pytest tests/test_auth.py -q
```

Run reservation tests only:

```bash
uv run pytest tests/test_reservations.py -q
```

---

# Docker

TableTurn uses Docker Compose for the main infrastructure services.

Services include:

```text
PostgreSQL
Redis
FastAPI application
```

The PostgreSQL container uses:

```text
postgres:16
```

Redis uses:

```text
redis:7
```

The application can be started with:

```bash
docker compose up -d
```

Check running containers:

```bash
docker compose ps
```

Stop the services:

```bash
docker compose down
```

---

# Environment Variables

The application uses environment variables for configuration and secrets.

Example:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/tableturn
SECRET_KEY=your-secret-key
PAYSTACK_SECRET_KEY=your-paystack-secret
FIREBASE_SERVICE_ACCOUNT=your-firebase-service-account
```

For Docker, a separate environment configuration is used.

Sensitive files such as `.env` and Firebase credentials should not be committed to Git.

---

# Running the Project Locally

## 1. Clone the repository

```bash
git clone <repository-url>
cd TABLETURN-Restaurant-Reservations-Kitchen-Orders
```

## 2. Install dependencies

The project uses `uv`.

```bash
uv sync
```

## 3. Configure environment variables

Create the required `.env` configuration and provide the necessary PostgreSQL, Redis, Paystack, and Firebase credentials.

## 4. Start infrastructure

```bash
docker compose up -d
```

## 5. Apply migrations

```bash
uv run alembic upgrade head
```

## 6. Start FastAPI

```bash
uv run fastapi dev app/main.py
```

The API documentation can then be accessed through the FastAPI Swagger interface.

## 7. Run tests

```bash
uv run pytest -q
```

---

# Major Challenges and Solutions

Building TableTurn involved several challenges beyond ordinary CRUD development.

## 1. Preventing Double Booking

### Challenge

A normal query could detect an existing reservation, but two requests arriving at almost the same time could both pass the check before either transaction completed.

That creates a race condition.

### Solution

The reservation service locks the relevant restaurant table row inside the transaction before checking for overlapping reservations.

The overlap check uses:

```text
new.start < existing.end
AND
new.end > existing.start
```

A concurrent test was added to verify that only one reservation succeeds.

---

## 2. Understanding Half-Open Time Intervals

### Challenge

The system needed to distinguish between genuine overlaps and reservations that simply touch.

For example:

```text
19:00–21:00
21:00–23:00
```

should be valid.

### Solution

The overlap formula was implemented using strict `<` and `>` comparisons.

This naturally allows the end of one reservation to equal the start of another.

---

## 3. Implementing the Kitchen State Machine

### Challenge

Without explicit transition rules, an order could move directly from an early state to a later state.

For example:

```text
NEW → READY
```

would incorrectly skip preparation.

### Solution

Valid transitions were explicitly defined in the kitchen service.

The service checks the current state and allows only the next valid state.

Invalid transitions return:

```text
409 Conflict
```

---

## 4. Real-Time Kitchen Updates

### Challenge

The kitchen needs to see new orders and status changes without repeatedly refreshing the page.

A traditional REST request alone would require polling.

### Solution

Firestore is used to store kitchen queue updates, while Server-Sent Events keep the kitchen client connected to the backend.

The SSE implementation listens for Firestore changes and forwards them to connected clients.

---

## 5. Testing SSE Without Creating Hanging Tests

### Challenge

SSE connections are intentionally long-lived.

An early test attempted to read another event when no event was available, causing the test to hang.

### Solution

The test was changed to provide a controlled queue containing a known event and to consume exactly the events that were available.

This allowed the SSE generator to be tested without relying on a real infinite connection.

---

## 6. Proving SSE Performance

### Challenge

The capstone expects kitchen updates to reach the stream quickly.

It is tempting to write a simple timer around an in-memory queue and claim that it proves sub-second Firestore-to-client latency.

That would not accurately represent production behavior.

### Solution

The automated test verifies the SSE event-delivery mechanism itself rather than making a misleading latency claim.

A true end-to-end latency measurement would require a running Firebase/Firestore environment and a real connected client.

---

## 7. Paystack Webhook Idempotency

### Challenge

A payment provider may send the same webhook more than once.

Processing the same event repeatedly could result in duplicate payment handling.

### Solution

Processed webhook event IDs are stored in PostgreSQL.

Before processing an event, the system checks whether its event ID has already been processed.

This makes the webhook operation idempotent.

---

## 8. Webhook Signature Verification

### Challenge

A webhook endpoint must not blindly trust incoming payment notifications.

An attacker could otherwise send a fake successful payment request.

### Solution

TableTurn verifies the Paystack `x-paystack-signature` using HMAC-SHA512 and the raw request body.

Invalid signatures are rejected with `401 Unauthorized`.

---

## 9. Manager and Staff Account Creation

### Challenge

The public registration endpoint should not allow someone to register themselves as a manager or kitchen user.

Allowing a client to submit:

```json
{
    "role": "manager"
}
```

would create a privilege-escalation vulnerability.

### Solution

Public registration does not accept a role.

Every public registration becomes a diner.

Managers have access to a separate staff creation endpoint that allows the creation of:

```text
WAITER
KITCHEN
MANAGER
```

This behavior is covered by automated tests.

---

## 10. Rate Limiting During Tests

### Challenge

Login is rate-limited to five requests per minute.

When the complete test suite ran, multiple tests shared the same client IP and therefore shared the rate limiter state.

Some unrelated reservation tests began receiving:

```text
429 Too Many Requests
```

### Solution

The production rate limit was left intact.

The pytest client fixture now resets the limiter before each test, giving every test isolated rate-limit state.

After the fix:

```text
36 passed
```

---

## 11. Keeping Historical Order Prices

### Challenge

A menu item's price can change after an order has been created.

If an order only referenced the current menu price, historical orders could display incorrect totals.

### Solution

Each `OrderItem` stores its own `unit_price`.

When an item is added to an order, the current menu price is copied into the order item.

The order therefore preserves the price that was actually used at the time.

---

## 12. Database and Docker Development

### Challenge

The application depends on PostgreSQL and Redis, while Firebase requires service-account credentials.

Running everything locally required coordinating several external services and environment variables.

### Solution

Docker Compose was used for PostgreSQL, Redis, and the application.

Firebase credentials are supplied through environment configuration rather than committed credential files.

This keeps infrastructure reproducible while protecting sensitive credentials.

---

# Security Considerations

TableTurn implements several security controls:

* Passwords are hashed with Argon2.
* Authentication uses JWT access tokens.
* Protected endpoints require authentication.
* Role-based access control restricts staff functionality.
* Public registration cannot create privileged accounts.
* Login is rate limited.
* Payment webhooks require signature verification.
* Duplicate payment events are handled idempotently.
* Secrets are stored through environment variables.
* Database credentials are not hard-coded into application logic.

---

# Project Status

The core capstone requirements have been implemented and tested.

Current status:

```text
Authentication & RBAC        ✓
Staff account provisioning   ✓
Reservations                 ✓
Overlap protection           ✓
Concurrency protection      ✓
Capacity validation          ✓
Reservation cancellation     ✓
Reservation seating          ✓
Orders                       ✓
Kitchen queue                ✓
Kitchen state machine        ✓
SSE                           ✓
Payments                     ✓
Paystack webhook             ✓
Webhook idempotency          ✓
Redis caching                ✓
Cache invalidation           ✓
Firestore floor feed        ✓
Turnover reporting           ✓
API contract                 ✓
Automated tests              ✓
Docker                       ✓
CI                            ✓
```

Test result:

```text
36 passed
```

Cloud deployment has not yet been completed.

---

# Lessons Learned

The project provided practical experience with problems that are difficult to solve correctly using basic CRUD operations.

The most important lessons were:

* Database transactions matter when multiple users can modify the same resource.
* Race conditions cannot always be solved with a simple existence check.
* Business rules belong in services where they can be reused and tested.
* State machines are useful when an entity must follow a controlled workflow.
* Webhooks must be authenticated and idempotent.
* Real-time systems require careful handling of long-lived connections.
* Tests must isolate shared state such as databases and rate limiters.
* Caching requires an invalidation strategy, not just a cache.
* Security decisions should be enforced on the server rather than trusted from client input.
* A passing test suite is useful evidence, but tests should only claim what they actually verify.

---

# Conclusion

TableTurn demonstrates a production-oriented restaurant backend that goes beyond basic CRUD functionality.

It combines transactional PostgreSQL operations for reservations and orders with Redis caching, Firebase Firestore for real-time data, SSE for live kitchen updates, JWT-based authentication, role-based authorization, and secure payment webhook processing.

The project currently has **36 passing automated tests** covering the major business rules and acceptance criteria of the capstone.
