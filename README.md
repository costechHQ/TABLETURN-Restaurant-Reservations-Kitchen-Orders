[![wakatime](https://wakatime.com/badge/user/cf5dfb0e-2b79-4a12-bcfd-ffd79a22a44f/project/2b4c39e6-27ea-4230-bcae-1a050ba2fbdf.svg)](https://wakatime.com/badge/user/cf5dfb0e-2b79-4a12-bcfd-ffd79a22a44f/project/2b4c39e6-27ea-4230-bcae-1a050ba2fbdf)

# TableTurn — Restaurant Reservations & Kitchen Display System

A backend system for managing restaurant table reservations, orders, kitchen workflows, payments, and real-time kitchen updates.

TableTurn is built around two operational problems that become especially difficult during busy restaurant service: **preventing table double-bookings under concurrent requests** and **keeping kitchen orders organized and traceable from placement to service**.

---

## Problem Statement

Busy restaurants face two major operational problems during peak periods such as the Friday rush.

### 1. Double-Booking Restaurant Tables

Restaurants have a limited number of tables, and multiple diners may attempt to reserve the same table for overlapping time periods.

A simple availability check is not enough. If two diners choose the same table at nearly the same time, both requests could potentially see the table as available and create conflicting reservations.

TableTurn solves this using **exact time-overlap checking** with half-open time windows:

```text
[start, end)
```

Two reservations overlap when:

```text
new.start < existing.end
AND
new.end > existing.start
```

This means two bookings may touch but cannot overlap.

For example:

```text
Reservation A: 17:00 ───── 18:00
Reservation B:                 18:00 ───── 19:00
```

These reservations are allowed because the first reservation ends exactly when the second begins.

The overlap check is performed inside a transaction while the table's reservations are locked. This prevents two diners attempting to reserve the same table and time slot concurrently from both successfully creating a booking.

---

### 2. Lost or Poorly Tracked Kitchen Orders

During a busy service, paper kitchen tickets can be lost, delayed, or difficult to track.

Waiters and kitchen staff may not have a shared view of whether an order is new, being prepared, or ready to serve.

TableTurn turns every order into a structured **kitchen ticket** with a controlled state machine:

```text
NEW → PREPARING → READY → SERVED
```

Kitchen staff can update the ticket as the order progresses.

Invalid state transitions are rejected with a `409 Conflict` response instead of allowing an order to jump between arbitrary states.

---

## Proposed Solution

TableTurn provides a centralized backend that connects restaurant reservations and kitchen operations.

The system:

* Prevents overlapping reservations for the same table.
* Uses half-open time intervals for precise reservation boundaries.
* Protects reservation creation against concurrent booking attempts.
* Manages restaurant tables and their capacities.
* Allows authorized users to create and manage reservations.
* Converts restaurant orders into structured kitchen tickets.
* Enforces a controlled kitchen order state machine.
* Provides real-time kitchen updates through Server-Sent Events (SSE).
* Supports menu management and order pricing.
* Records payments and processes payment webhook events.
* Uses role-based access control for different restaurant users.
* Provides reporting capabilities for restaurant management.

---

# Core Features

## Authentication & Authorization

TableTurn uses JWT-based authentication and role-based access control.

Supported roles include:

| Role      | Responsibility                                            |
| --------- | --------------------------------------------------------- |
| `DINER`   | Make and manage personal reservations                     |
| `WAITER`  | Create restaurant orders and manage waiter operations     |
| `KITCHEN` | Process kitchen orders and update ticket status           |
| `MANAGER` | Manage restaurant resources and administrative operations |

Protected endpoints verify both authentication and the user's assigned role.

---

## Table Management

Restaurant tables contain:

* Table ID
* Table code
* Seating capacity

Tables are used as the foundation for the reservation system.

The reservation service checks the table's capacity before accepting a booking.

Example:

```json
{
  "code": "T01",
  "capacity": 4
}
```

---

## Reservation Management

Reservations contain:

* Table
* Diner
* Party size
* Start time
* End time
* Reservation status

Supported reservation states include:

```text
CONFIRMED
SEATED
CANCELLED
```

### Exact Overlap Detection

TableTurn uses the following rule:

```text
new.start < existing.end
AND
new.end > existing.start
```

This correctly handles adjacent bookings while preventing actual overlaps.

### Concurrency Protection

Reservation creation is performed transactionally with the relevant table reservations locked.

The goal is to prevent this race condition:

```text
Diner A ── checks table ── available
                         \
                          creates reservation

Diner B ── checks table ── available
                         \
                          creates reservation
```

Both requests must not be allowed to win for the same overlapping slot.

---

# Order Management

Waiters can create orders for restaurant tables and add menu items to those orders.

Each order contains its associated ordered items and tracks the total amount.

Order items contain:

* Menu item
* Quantity
* Unit price
* Notes
* Preparation status

The menu item's price is captured as the order item's `unit_price`, creating a price snapshot for the transaction.

This is important because a future menu price change should not alter the price of an item that was already ordered.

---

# Kitchen Display System

Every order becomes a kitchen ticket.

The kitchen workflow is:

```text
NEW
 ↓
PREPARING
 ↓
READY
 ↓
SERVED
```

The state machine prevents invalid transitions.

For example:

```text
NEW → PREPARING       ✓
PREPARING → READY     ✓
READY → SERVED        ✓
NEW → READY           ✗
SERVED → PREPARING    ✗
```

Invalid transitions return:

```text
409 Conflict
```

This keeps the kitchen workflow predictable and prevents inconsistent order states.

---

# Real-Time Kitchen Updates

TableTurn provides a live kitchen feed using **Server-Sent Events (SSE)**.

Kitchen clients can maintain a connection to the server and receive updates when relevant order activity occurs.

This avoids requiring kitchen staff to repeatedly refresh the page to discover changes.

The main endpoints include:

```text
GET /api/v1/kitchen/queue
GET /api/v1/kitchen/stream
```

The queue provides the current kitchen workload, while the stream provides live updates.

---

# Menu Management

Menu items contain:

* Name
* Description
* Price
* Availability

Menu validation prevents invalid values such as non-positive prices and descriptions outside the defined length constraints.

Redis caching is used to reduce unnecessary database reads for menu data, with cache invalidation when relevant menu information changes.

---

# Payments

TableTurn provides payment records associated with restaurant orders.

Payment records track:

* Order
* Amount
* Payment method
* Payment timestamp
* Payment status

Supported payment states include:

```text
PENDING
SUCCESS
FAILED
```

The system also supports Paystack webhook processing.

Webhook requests are verified using the request's raw body and the Paystack signature before the event is processed.

Processed events are tracked to support webhook idempotency and prevent the same event from being processed repeatedly.

---

# Reporting

The system provides reporting functionality for restaurant management.

Reports can use successful payment records to calculate restaurant turnover for a specified period.

This provides management with useful financial information without requiring direct access to raw database records.

---

# Architecture

TableTurn follows a layered backend architecture:

```text
Client
  │
  ▼
FastAPI Routes
  │
  ▼
Schemas / Validation
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

Supporting services include:

```text
Redis       → caching
Firestore   → kitchen/live event data
Paystack    → payment processing
SSE         → real-time kitchen updates
```

The application separates HTTP handling from business logic so that complex rules such as reservation conflict detection and kitchen state transitions remain inside service layers.

---

# Technology Stack

| Technology           | Purpose                                      |
| -------------------- | -------------------------------------------- |
| Python               | Backend programming language                 |
| FastAPI              | REST API framework                           |
| SQLModel             | ORM and data modelling                       |
| PostgreSQL           | Primary relational database                  |
| Alembic              | Database migrations                          |
| Redis                | Caching                                      |
| Firebase / Firestore | Real-time kitchen data                       |
| Server-Sent Events   | Live kitchen updates                         |
| JWT                  | Authentication                               |
| Argon2               | Password hashing                             |
| Paystack             | Payment integration                          |
| Docker               | Containerized development                    |
| pytest               | Automated testing                            |
| uv                   | Python dependency and environment management |

---

# Project Structure

```text
tableturn/
│
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── deps.py
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
│   └── services/
│       ├── auth_service.py
│       ├── reservation_service.py
│       ├── menu_service.py
│       ├── order_service.py
│       ├── kitchen_service.py
│       ├── payment_service.py
│       ├── webhook_service.py
│       └── report_service.py
│
├── alembic/
├── tests/
├── docker-compose.yml
├── pyproject.toml
├── alembic.ini
├── .env.example
└── README.md
```

---

# API Overview

The API is organized around the following resources:

| Resource        | Purpose                         |
| --------------- | ------------------------------- |
| `/auth`         | Registration and authentication |
| `/tables`       | Restaurant table management     |
| `/reservations` | Reservation management          |
| `/menu`         | Menu item management            |
| `/orders`       | Order creation and management   |
| `/kitchen`      | Kitchen queue and live updates  |
| `/payments`     | Payment records                 |
| `/webhook`      | Payment webhook processing      |
| `/reports`      | Restaurant reporting            |

Interactive API documentation is available through FastAPI's generated documentation when the application is running.

---

# Database Design

The main entities are:

```text
User
 │
 ├── Reservation
 │       │
 │       └── RestaurantTable
 │
 └── Order
        │
        ├── OrderItem
        │       │
        │       └── MenuItem
        │
        └── Payment
```

A separate `ProcessedEvent` entity is used to track processed webhook events and support idempotent event handling.

---

# Running the Project

## Requirements

* Python 3.14+
* uv
* Docker
* Docker Compose

## 1. Clone the repository

```bash
git clone <repository-url>
cd TABLETURN-Restaurant-Reservations-Kitchen-Orders
```

## 2. Install dependencies

```bash
uv sync
```

## 3. Configure environment variables

Create a local `.env` file from the provided example:

```bash
cp .env.example .env
```

Configure your local values:

```env
DATABASE_URL=<your-database-url>
SECRET_KEY=<your-secret-key>
PAYSTACK_SECRET_KEY=<your-paystack-secret>
```

Never commit real credentials to the repository.

## 4. Start infrastructure

```bash
docker compose up -d
```

This starts the required development infrastructure such as PostgreSQL and Redis.

## 5. Run migrations

```bash
uv run alembic upgrade head
```

## 6. Start the API

```bash
uv run fastapi dev
```

The API documentation will then be available through the FastAPI development server.

---

# Environment Variables

Sensitive configuration is supplied through environment variables.

Example `.env.example`:

```env
DATABASE_URL=<your-database-url>
SECRET_KEY=<your-secret-key>
PAYSTACK_SECRET_KEY=<your-paystack-secret>
```

No real database passwords, JWT secrets, Paystack keys, Firebase credentials, or other private credentials should be stored in:

* `README.md`
* `.env.example`
* source code
* screenshots
* public documentation
* Git history

---

# Testing

The project uses `pytest` for automated testing.

Tests are intended to cover the system's critical business rules, particularly:

* Authentication
* Role-based authorization
* Table management
* Reservation creation
* Reservation overlap detection
* Reservation concurrency
* Reservation cancellation
* Menu validation
* Order creation
* Order totals
* Kitchen state transitions
* Payment processing
* Webhook signature verification
* Webhook idempotency
* Kitchen/SSE behaviour

Run the test suite with:

```bash
uv run pytest
```

---

# Error Handling

TableTurn uses appropriate HTTP responses for different classes of failures.

Examples include:

| Status | Meaning                  |
| ------ | ------------------------ |
| `400`  | Invalid request          |
| `401`  | Authentication required  |
| `403`  | Insufficient permissions |
| `404`  | Resource not found       |
| `409`  | Business-rule conflict   |
| `422`  | Validation error         |
| `500`  | Unexpected server error  |

A `409 Conflict` is particularly important for business rules such as invalid kitchen state transitions and reservation conflicts.

---

# Security

The application includes several security mechanisms:

* JWT authentication
* Password hashing
* Role-based access control
* Protected routes
* Environment-based secrets
* Paystack webhook signature verification
* Webhook idempotency tracking
* Input validation
* Database transactions for critical operations

Secrets are intentionally excluded from public project documentation.

---

# Development Workflow

The project uses Git branches to separate feature development.

Typical workflow:

```text
main
 │
 ├── feature/auth
 ├── feature/reservations
 ├── feature/menu
 ├── feature/orders
 └── feature/kitchen
```

Features are developed and tested independently before being merged into the main branch.

---

# Project Objectives

The project aims to demonstrate practical backend engineering skills through a real-world restaurant workflow.

The main objectives are to:

1. Build a structured REST API using FastAPI.
2. Model relational restaurant data using SQLModel and PostgreSQL.
3. Implement secure authentication and role-based authorization.
4. Solve exact reservation overlap detection.
5. Handle concurrent reservation attempts safely.
6. Implement a controlled kitchen order state machine.
7. Provide real-time kitchen updates.
8. Integrate payment processing and secure webhooks.
9. Use caching to improve frequently accessed data.
10. Apply database migrations using Alembic.
11. Containerize development infrastructure with Docker.
12. Test important business rules with automated tests.

---

# Current Development Status

TableTurn is an active capstone project under development.

### Implemented / Substantially Implemented

* Authentication and JWT authorization
* Role-based access control
* Restaurant table management foundation
* Reservation management
* Exact reservation overlap detection
* Reservation capacity validation
* Reservation status management
* Menu management
* Redis caching
* Order management foundation
* Order item pricing snapshots
* Kitchen order workflow
* SSE kitchen feed foundation
* Payment records
* Paystack webhook verification foundation
* Webhook event tracking
* PostgreSQL and Docker infrastructure
* Alembic migrations

### Remaining / Under Final Verification

* Full asynchronous database implementation
* Complete automated test coverage
* Final order authorization audit
* Complete table CRUD verification
* Payment/webhook hardening
* Comprehensive SSE testing
* CI/CD verification
* Final security and dependency audit
* Final API and documentation review

The status above is intentionally separated so the documentation reflects the actual development state rather than presenting unfinished functionality as production-ready.

---

# Learning Outcomes

Through TableTurn, the project demonstrates practical experience with:

* REST API development
* FastAPI
* SQLModel
* PostgreSQL
* Database transactions
* Concurrency control
* Time-interval algorithms
* Authentication and authorization
* State machines
* Real-time communication
* Redis caching
* Payment webhooks
* Idempotent event processing
* Database migrations
* Docker
* Automated testing
* Layered backend architecture

---

# Key Technical Challenge

The central technical challenge of TableTurn is not simply creating a reservation endpoint.

It is ensuring that **the same limited restaurant table cannot be successfully allocated to two overlapping reservations, even when requests arrive concurrently**.

The system therefore combines:

```text
Exact interval mathematics
        +
Transactional database operations
        +
Row-level locking
        +
Validation
```

with a second workflow that converts:

```text
Restaurant Order
       ↓
Kitchen Ticket
       ↓
NEW
       ↓
PREPARING
       ↓
READY
       ↓
SERVED
```

This combination forms the core engineering problem behind TableTurn.

---

# Project Goal

TableTurn aims to provide a reliable backend foundation for restaurant operations by solving two high-impact problems:

**Preventing table double-bookings through exact, concurrency-safe reservation handling, while replacing unreliable paper kitchen tickets with a structured and real-time digital kitchen workflow.**

The result is a backend architecture that connects the restaurant's **tables, reservations, orders, kitchen, menu, and payments** into a single system.

