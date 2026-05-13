# Attendance System Pro

A modern, mobile-first HR management system built on a 3-tier architecture. Employees can clock in/out, request leave, and manage their profiles — all through a lightweight PWA that integrates seamlessly with Odoo 18 ERP as the data backbone.

---

## Overview

**Attendance System Pro** acts as an intelligent proxy layer between end users and Odoo ERP. Rather than granting every employee a full Odoo license, this system exposes a clean, role-based interface for the most common HR operations while keeping Odoo as the single source of truth.

### Key Features

- **Attendance** — Check-in / Check-out with GPS location, live timer, history log, and monthly summary.
- **Leave Management** — Submit leave requests, track remaining balance, and view approval history. Managers get a dedicated approval panel.
- **Employee Profile** — View and update personal information. Read-only contract details sourced directly from Odoo.
- **Admin Panel** — Full user CRUD with search, role management, and account activation.
- **License Efficiency** — The FastAPI backend authenticates locally and communicates with Odoo via XML-RPC using a single service account, reducing the number of required Odoo user licenses.

### User Roles

| Role | Access |
|---|---|
| Employee | Attendance, Leave, Profile |
| Manager | All employee features + Leave approval + Team view |
| Admin | All features + User management |

---

## Architecture

```
┌─────────────────────────────┐
│   React PWA (Mobile-first)  │  ← Frontend (Vite + antd-mobile)
│   http://localhost:5173     │
└────────────┬────────────────┘
             │ REST / JWT
┌────────────▼────────────────┐
│   FastAPI Backend           │  ← Business logic + local auth
│   http://localhost:8000     │
│   PostgreSQL (local auth)   │
└────────────┬────────────────┘
             │ XML-RPC
┌────────────▼────────────────┐
│   Odoo 18 ERP               │  ← HR data source of truth
│   http://localhost:8069     │
└─────────────────────────────┘
```

---

## Tech Stack

### Frontend
| Technology | Purpose |
|---|---|
| React 19 + TypeScript | UI framework |
| Vite 8 + vite-plugin-pwa | Build tool + PWA support |
| antd-mobile | Mobile-first UI components |
| TanStack React Query | Server state management |
| React Router v7 | Client-side routing |
| Axios | HTTP client with JWT interceptor |
| dayjs | Date handling |

### Backend
| Technology | Purpose |
|---|---|
| FastAPI | REST API framework |
| SQLAlchemy + PostgreSQL | Local user auth storage |
| python-jose | JWT token generation & validation |
| passlib / bcrypt | Password hashing |
| requests | Odoo XML-RPC communication |

### Infrastructure
| Technology | Purpose |
|---|---|
| Docker + Docker Compose | Container orchestration |
| Odoo 18 | Core HR data layer |

---

## Getting Started

### Option 1: Docker (Recommended)

Packages the backend and database together — no manual dependency setup required.

**Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop)

**Step 1 — Configure environment**

Create a `.env` file inside the `backend/` directory:

```env
DATABASE_URL=postgresql://bestmix_user:bestmix_pass@db/bestmix_auth_db
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=60
ODOO_URL=http://host.docker.internal:8069
ODOO_DB=your_odoo_db_name
ODOO_USER=your_odoo_admin_email
ODOO_PASSWORD=your_odoo_admin_password
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=changeme
```

> `host.docker.internal` allows the Docker container to reach Odoo running on the host machine. On Linux, you may need to add `--add-host=host.docker.internal:host-gateway` or use the host IP directly.

**Step 2 — Start services**

From the project root:

```bash
docker-compose up -d --build
```

This will:
1. Start a PostgreSQL 15 container (local auth DB).
2. Build and run the FastAPI backend.

**Step 3 — Access**

| Service | URL |
|---|---|
| Backend API | http://localhost:8000 |
| Interactive API Docs | http://localhost:8000/docs |

---

### Option 2: Manual Setup

Useful for development or debugging.

#### Backend

**Prerequisites:** Python 3.10+

```bash
# 1. Navigate to backend directory
cd backend

# 2a. Create and activate virtualenv (venv)
python -m venv venv
source venv/bin/activate          # macOS / Linux
# .\venv\Scripts\activate         # Windows PowerShell

# 2b. Or use Conda
# conda create --name attendance-env python=3.10
# conda activate attendance-env

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
# Create backend/.env (see Docker section above for variables)
# Set DATABASE_URL to your local PostgreSQL instance:
# DATABASE_URL=postgresql://user:password@localhost/dbname
# Set ODOO_URL=http://localhost:8069

# 5. Run the server
uvicorn app.main:app --reload
```

> You need a running PostgreSQL instance. The application creates tables and seeds the initial admin account automatically on first startup.

#### Frontend

**Prerequisites:** Node.js 18+

```bash
cd frontend
npm install
npm run dev
```

Access the frontend at `http://localhost:5173`.

---

## Project Structure

```
attendance-system-pro/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints/      # Route handlers (auth, users, attendance, leave, profile)
│   │   ├── core/               # Config, database, security, logging
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   └── services/           # Business logic + Odoo XML-RPC calls
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/                # Axios client + endpoint functions
│   │   ├── components/         # Shared UI components
│   │   ├── contexts/           # Auth + App React contexts
│   │   ├── hooks/              # Custom React hooks
│   │   ├── pages/              # Route-level page components
│   │   │   ├── attendance/
│   │   │   ├── leave/
│   │   │   ├── profile/
│   │   │   └── admin/
│   │   └── types/              # TypeScript type definitions
│   ├── public/
│   └── vite.config.ts
├── docker-compose.yml
├── docs/
└── openspec/
```

---

## API Reference

Full interactive documentation is available at `http://localhost:8000/docs` (Swagger UI) once the backend is running.

### Endpoint Summary

| Module | Method | Endpoint | Description |
|---|---|---|---|
| Auth | POST | `/auth/login` | Obtain JWT access token |
| Auth | POST | `/auth/logout` | Invalidate session |
| Auth | POST | `/auth/refresh` | Refresh access token |
| Auth | POST | `/auth/forgot-password` | Send password reset email |
| Auth | POST | `/auth/reset-password` | Reset password via token |
| Attendance | GET | `/attendance/status` | Current check-in status |
| Attendance | POST | `/attendance/check-in` | Clock in |
| Attendance | POST | `/attendance/check-out` | Clock out |
| Attendance | GET | `/attendance/history` | Attendance log |
| Attendance | GET | `/attendance/summary` | Monthly summary |
| Leave | GET | `/leave/balance` | Remaining leave balance |
| Leave | GET | `/leave/types` | Available leave types |
| Leave | POST | `/leave/request` | Submit a leave request |
| Leave | GET | `/leave/history` | Leave request history |
| Leave | GET | `/leave/pending` | Pending approvals (manager) |
| Leave | POST | `/leave/{id}/approve` | Approve a leave request |
| Leave | POST | `/leave/{id}/reject` | Reject a leave request |
| Profile | GET | `/profile/` | Get employee profile |
| Profile | PUT | `/profile/` | Update profile |
| Profile | GET | `/profile/contract` | View contract details |
| Users | GET | `/users/` | List all users (admin) |
| Users | POST | `/users/` | Create user (admin) |
| Users | PUT | `/users/{id}` | Update user (admin) |
| Users | DELETE | `/users/{id}` | Delete user (admin) |
| Users | GET | `/users/team` | View team members (manager) |

---

## License

[MIT](LICENSE)
