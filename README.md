# Secure REST API — Project 6

Portfolio-ready FastAPI authentication API using **Argon2id**, signed **JWT access tokens**, SQLAlchemy, Alembic migrations, role-based access, and pytest.

## Quick start (macOS / Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Paste the generated random secret into `.env` as `JWT_SECRET_KEY`.

```bash
alembic upgrade head
python -m pytest -q
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs.

## API endpoints

| Method | Path | Access |
|---|---|---|
| GET | `/health` | Public |
| POST | `/auth/register` | Public |
| POST | `/auth/login` | Public; OAuth2 **form** using email as `username` |
| GET | `/auth/me` | Bearer token |
| GET | `/admin/users` | Admin-only |

Use Swagger UI's **Authorize** dialog with your registered email/password to obtain a token. Registration always creates the **user** role; clients cannot self-register as admins. The admin endpoint is covered by tests using a test-only role assignment. No public endpoint promotes accounts to admin.

## Architecture

- `app/routers/`: HTTP endpoints and status codes
- `app/security.py`: Argon2 password hashing and JWT verification
- `app/dependencies.py`: identity and role-based access checks
- `app/models.py`, `app/schemas.py`: database model and public DTOs
- `alembic/`: production database schema migrations
- `tests/`: isolated in-memory SQLite database, no production database access

## Security notes

This is a learning portfolio project, **not yet a fully hardened public authentication service**. Before internet deployment add TLS, rate limiting, abuse protection, audit logs, email verification, password recovery, user lifecycle management, token revocation/rotation, and production secret management. Do not use real passwords in demos. The admin list is capped at 100 rows for demonstration; production pagination is needed. Keep `.env` and local `.db` files out of Git.

## Development roadmap

1. Complete registration/login and test authorization (this milestone).
2. Add RBAC policies, secure admin bootstrap, comprehensive negative tests.
3. Switch to PostgreSQL, add Docker, GitHub Actions, observability, and deployment.
