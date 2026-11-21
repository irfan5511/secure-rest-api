# Secure REST API

**FastAPI authentication and role-based access control, with PostgreSQL, Docker, Alembic, automated tests, and a live cloud deployment.**

[**Live API documentation (Swagger UI)**](https://secure-rest-api-iota.vercel.app/docs) · [**Health endpoint**](https://secure-rest-api-iota.vercel.app/health)

> **Portfolio demonstration, not a production-hardened identity service.** Use disposable test accounts and passwords only. Do not store real or sensitive user information.

## Overview

A Python REST API demonstrating how to implement user registration, password hashing, JWT-based authentication, protected endpoints, and role-based authorization. The application uses SQLAlchemy for persistence and Alembic for versioned schema migrations.

The same application runs locally with **Docker Compose + PostgreSQL** and is deployed publicly using **Vercel's Python/FastAPI runtime + Neon PostgreSQL**. The Vercel deployment does **not** run the Docker image; Docker remains part of the local, portable deployment workflow.

### Key features

- **Authentication:** user registration, OAuth2 password-form login, signed JWT bearer access tokens, and authenticated profile retrieval.
- **Password handling:** Argon2 password hashing; plaintext passwords are not returned by the API.
- **Authorization:** regular `user` and `admin` roles; admin-only route protected by a role-check dependency.
- **Persistence:** SQLAlchemy models and PostgreSQL; Alembic database migrations.
- **Local infrastructure:** Dockerfile, Docker Compose, PostgreSQL health check, persistent database volume.
- **Continuous integration:** GitHub Actions workflow that provisions PostgreSQL, runs Alembic migrations, and executes automated tests.
- **Testing:** 14 passing pytest tests using an isolated SQLite test database. CI additionally validates PostgreSQL schema migration.
- **Cloud demo:** publicly reachable HTTPS API on Vercel, backed by a Neon-hosted PostgreSQL database.

## Technology stack

| Area | Technology |
| --- | --- |
| Web API | Python, FastAPI, Uvicorn |
| Authentication | OAuth2 password flow, PyJWT, Argon2 |
| Data access | SQLAlchemy |
| Database | PostgreSQL (local Docker and Neon cloud); SQLite (isolated tests) |
| Schema migrations | Alembic |
| Validation/configuration | Pydantic, pydantic-settings |
| Containers | Docker, Docker Compose |
| CI | GitHub Actions, pytest |
| Cloud runtime | Vercel Python/FastAPI runtime |
| Managed cloud database | Neon PostgreSQL |

## Architecture

```text
                GitHub repository
                      |
           GitHub Actions CI checks
                      |
            +---------+---------+
            |                   |
        Local setup          Cloud demo
            |                   |
      Docker Compose        Vercel HTTPS
         /      \            FastAPI
     FastAPI  PostgreSQL         |
            |                Neon PostgreSQL
         Alembic                |
                              Alembic
                       (run separately)
```

Both environments use the same FastAPI application and Alembic migration history. The cloud database schema is migrated explicitly; database migrations are **not** automatically executed by Vercel serverless functions.

## API endpoints

| Method | Endpoint | Access | Expected success |
| --- | --- | --- | --- |
| `GET` | `/health` | Public | `200 OK` |
| `POST` | `/auth/register` | Public | `201 Created` |
| `POST` | `/auth/login` | Public; OAuth2 form (`username` = email) | `200 OK` |
| `GET` | `/auth/me` | Valid bearer token | `200 OK` |
| `GET` | `/admin/users` | Admin role | `200 OK` |

**Authorization behavior:** unauthenticated access to protected routes returns `401`; an authenticated non-admin requesting `/admin/users` receives `403`. Registration always creates the regular `user` role. No public API endpoint allows users to promote themselves to admin.

### Try the live demo

1. Open [Swagger UI](https://secure-rest-api-iota.vercel.app/docs).
2. Register an **invented, disposable** test account using `POST /auth/register` and a unique password used nowhere else.
3. Click **Authorize** in Swagger and use the registered email in the `username` field and your test password. Swagger obtains a token via `POST /auth/login`.
4. Execute `GET /auth/me` to verify authenticated access.
5. Execute `GET /admin/users` with the same regular account; it should return `403 Forbidden`.

Do not post login credentials, bearer tokens, connection strings, or environment secrets in screenshots, issues, or chat messages.

## Run locally with Docker Compose

**Prerequisites:** Docker Desktop or Docker Engine with Compose.

```bash
# Clone the repository
git clone https://github.com/irfan5511/secure-rest-api.git
cd secure-rest-api

# Create the local configuration file
cp .env.example .env
```

Set a **random** `JWT_SECRET_KEY` of at least 32 characters and add a separate `POSTGRES_PASSWORD` to `.env`. Generate secure values using:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Example `.env` structure (replace placeholders with different generated values):

```dotenv
DATABASE_URL=sqlite:///./secure_api.db
JWT_SECRET_KEY=REPLACE_WITH_RANDOM_SECRET_AT_LEAST_32_CHARACTERS
JWT_ALGORITHM=HS256
ACCESS_TOKEN_MINUTES=30
POSTGRES_PASSWORD=REPLACE_WITH_SEPARATE_RANDOM_POSTGRES_PASSWORD
```

The local `DATABASE_URL` example is for host-based development; **Docker Compose overrides it** with a PostgreSQL URL for the API container.

Start the containers:

```bash
docker compose up --build -d
docker compose ps
curl http://127.0.0.1:8000/health
```

The API is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). The API container runs `alembic upgrade head` before starting Uvicorn.

Inspect database state:

```bash
docker compose exec api alembic current
docker compose exec db psql -U secure_api -d secure_api -c '\dt'
```

Shut down the stack without deleting persistent database data:

```bash
docker compose down
```

## Python development and automated tests

Using Python 3.13 or a compatible Python version:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

The test suite uses an isolated SQLite database and does not modify the local Docker database or the Neon cloud database. The GitHub Actions workflow separately starts PostgreSQL and checks Alembic migration execution.

## Cloud deployment: Vercel + Neon

The deployed application is served by the Vercel Python runtime, using the root-level `main.py` entry point importing `app` from `app.main`. Cloud deployment does not use `compose.yaml` or the Dockerfile.

Required **Production** environment variables in Vercel:

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | Private Neon PostgreSQL pooled connection string, using the `postgresql+psycopg://` SQLAlchemy driver prefix; retain Neon's SSL query options |
| `JWT_SECRET_KEY` | Independently generated random secret, minimum 32 characters |
| `JWT_ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_MINUTES` | `30` |

Apply migrations to the Neon database **before** testing database-backed endpoints. Use a Neon **direct (non-pooled)** connection string to run Alembic from a trusted development environment, without saving credentials in Git or revealing them in terminal logs. Use the pooled connection string for the Vercel application. Database name and role are assigned by Neon; the demonstration database uses `neondb`.

A Vercel redeployment is needed when changing production environment variables. Never commit `.env` or include credentials in the README.

## Repository structure

```text
app/
  main.py               # FastAPI app and routers
  config.py             # Settings from environment
  database.py           # SQLAlchemy engine and session
  models.py             # User database model
  schemas.py            # Request/response schemas
  security.py           # Password hashing and JWTs
  dependencies.py       # Authenticated user and admin checks
  routers/
    auth.py             # Register, login, profile
    admin.py            # Admin-only user listing
alembic/                # Database migration history
tests/                  # Isolated API/auth tests
.github/workflows/      # GitHub Actions CI
Dockerfile              # Container image for local/portable deployment
compose.yaml            # Local API + PostgreSQL stack
main.py                 # Vercel FastAPI entry point
requirements.txt
```

A local `promote_admin.py` utility may be used by a trusted operator to assign the initial admin role. It is **not** a public HTTP endpoint. When running administrative scripts, confirm which database the active `DATABASE_URL` points to; running a local script does not automatically change the cloud database. Do not automatically run admin promotion during startup.

## Verification completed

The following checks were performed during development and deployment:

- Local Docker API health endpoint returned `200 OK`.
- Dockerized PostgreSQL became healthy; Alembic reported `0001_create_users (head)`.
- The database contained `users` and `alembic_version` tables.
- All **14 pytest tests** passed locally.
- GitHub Actions **Backend CI** completed successfully.
- Neon migration completed with revision `0001_create_users (head)`.
- Vercel cloud `/health` returned `{"status":"ok"}`.
- Live user registration returned `201`; JWT login and `/auth/me` returned `200`.
- Live unauthenticated `/admin/users` returned `401`; authenticated regular-user access returned `403`.

These checks establish the behavior of the demonstrated flows; they do **not** constitute a security audit or a production-readiness certification.

## Security and operational limitations

This project is intended as an **engineering portfolio demo**, not as a service for real user identities or sensitive data. Before broader production use, additional work is required, including:

- Login/registration rate limiting and automated abuse prevention.
- Email verification, secure password recovery, and user lifecycle management.
- Token revocation/rotation and a defined session-management strategy.
- Audit logging, monitoring, alerting, and incident-response procedures.
- Managed secret rotation, least-privilege access, and database backup/restore planning.
- Security testing, dependency maintenance, and operational review.
- Pagination and tighter access controls for administrative user listings (currently capped at 100 records).

HTTPS is provided by the cloud host for the live demonstration. Avoid real passwords, real user data, and permanently privileged test accounts.

## License

No license is declared in this README; refer to the repository for any applicable license file.