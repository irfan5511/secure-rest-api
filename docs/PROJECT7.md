# Project 7 — Docker, PostgreSQL and CI

This upgrade adds containerized PostgreSQL and GitHub Actions to the existing
**secure-rest-api** project. It does not change your existing authentication routes.

## 1. Prepare Docker Desktop

Install Docker Desktop for your Mac from https://docs.docker.com/desktop/setup/install/mac-install/
Open Docker Desktop and verify that the Docker engine is running:

```sh
docker --version
docker compose version
```

## 2. Install the PostgreSQL driver

In your project directory with `.venv` activated:

```sh
python -m pip install 'psycopg[binary]>=3.2,<4'
python -m pip freeze | grep -i psycopg
```

Add this line to `requirements.txt` (do not remove existing dependencies):

```text
psycopg[binary]>=3.2,<4
```

## 3. Add Docker database password to your existing `.env`

You already have a JWT secret in `.env`. Do not overwrite it. Add:

```env
POSTGRES_PASSWORD=YOUR_NEW_RANDOM_POSTGRES_PASSWORD
```

Generate one locally:

```sh
python -c 'import secrets; print(secrets.token_hex(24))'
```

Use only letters and digits for this password because the database URL in
`compose.yaml` embeds it; this avoids URL escaping problems. Never commit `.env`.

## 4. Start PostgreSQL and FastAPI together

```sh
docker compose up --build -d
docker compose ps
docker compose logs --tail=80 api
curl -i http://127.0.0.1:8000/health
```

Expected health response: `{"status":"ok"}`.
Swagger documentation: http://127.0.0.1:8000/docs

The container runs `alembic upgrade head` before starting the API. PostgreSQL
persists in the named volume `postgres_data`; the database is not published to
host ports. The API is bound to localhost only.

## 5. Check migration

```sh
docker compose exec api alembic current
docker compose exec db psql -U secure_api -d secure_api -c '\dt'
```

The `users` and `alembic_version` tables should appear.

## 6. Run existing tests locally

```sh
python -m pytest -q
```

Existing tests use isolated SQLite for speed; CI independently checks the
actual migrations on PostgreSQL before running the tests. This is not the same
as a full PostgreSQL integration test suite.

## 7. Push to GitHub and check CI

```sh
git status
git add Dockerfile compose.yaml .dockerignore .github/workflows/ci.yml docs/PROJECT7.md requirements.txt
git commit -m 'Add Docker PostgreSQL and GitHub Actions CI'
git push
```

Open your GitHub repository > Actions > Backend CI. CI should migrate the
PostgreSQL database and run your test suite.

## Troubleshooting

- `docker: command not found`: install Docker Desktop and open it.
- `address already in use`: stop the previous local uvicorn service on port 8000.
- `JWT_SECRET_KEY` missing: check `.env` contains a randomly generated secret.
- `POSTGRES_PASSWORD` missing: add it to `.env`.
- Containers fail: `docker compose logs db` and `docker compose logs api`.
- `psycopg` driver missing: add the dependency to `requirements.txt` and rebuild.

## Shut down

```sh
docker compose down
```

Do **not** add `-v` unless you intentionally want to delete PostgreSQL data.

## Security scope

Local Docker and CI do not make this authentication service safe for public
internet exposure. Before cloud deployment add appropriate abuse controls,
TLS, a managed database, secret management, audit logging and token/session
lifecycle security. This project milestone deliberately stays local.
