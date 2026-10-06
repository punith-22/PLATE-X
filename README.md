# PLATE-X

**Vehicle Investigation & Intelligence Framework**

Developed by **Punith Kumar M G**.

PLATE-X is a privacy-first investigation workspace for vehicle-registration validation, lawful case management, evidence integrity, auditability and role-based access control. It intentionally does **not** expose a public vehicle-owner lookup.

## Features

- Indian registration normalization and format validation
- State/RTO identification
- JWT authentication
- RBAC: admin, investigator, viewer
- Case management with SQLite persistence
- Evidence records with SHA-256 integrity hashes
- Append-style audit events for investigation actions
- Admin user management
- React + Vite dashboard
- CORS configuration for local development
- OpenAPI documentation through FastAPI

## Quick start

### 1. Backend

Requirements: Python 3.11+ recommended.

~~~bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
~~~

Create environment variables from the example:

~~~bash
cp ../.env.example .env
~~~

Set at minimum:

- `PLATE_X_JWT_SECRET`: random secret, 32+ characters
- `PLATE_X_ADMIN_USERNAME`: initial administrator username
- `PLATE_X_ADMIN_PASSWORD`: strong initial administrator password

Run:

~~~bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
~~~

The API is available at `http://127.0.0.1:8000` and Swagger UI at `http://127.0.0.1:8000/docs`.

### 2. Frontend

~~~bash
cd frontend
npm install
cp .env.example .env
npm run dev
~~~

Open the Vite address shown in the terminal, normally `http://127.0.0.1:5173`.

## First login

The first backend start creates the configured admin account. Use the username/password from your local environment file. Do not commit `.env` or real credentials.

## Roles

- **admin**: users, audit, cases, evidence and investigation access
- **investigator**: vehicle investigation, cases and evidence
- **viewer**: read-only investigation access

## Security notes

PLATE-X is designed for authorized investigations and training. Private owner identity data is not returned by the built-in vehicle endpoint. Any future authoritative provider integration must enforce lawful authorization, least privilege, provider terms, audit logging and field minimization.

For production deployment, replace SQLite with a managed database, put the API behind TLS, use an HttpOnly secure session/cookie strategy, add CSRF protection where cookie auth is used, add rate limiting, backups, secret management, malware scanning for uploaded files, and a proper object store for evidence.

## API

- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/vehicles/{registration}`
- `POST/GET /api/v1/cases`
- `POST/GET /api/v1/evidence`\n- `POST /api/v1/evidence/upload` (multipart, 25 MiB limit)
- `GET /api/v1/audit` (admin)
- `GET/POST /api/v1/users` (admin)
