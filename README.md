# FastAPI Template

## Stack
- FastAPI for the API layer.
- SQLModel for ORM models and database access.
- Alembic for migrations.
- PostgreSQL (default in settings/compose) and SQLite for local Alembic config.
- Redis + Celery for background tasks.
- fastapi-mail for email delivery.
- Docker and Docker Compose for local services.

## Repo structure
- `src/` application code.
- `src/core/` shared helpers (auth, database, dependencies, fixtures, selectors).
- `src/modules/` feature modules (auth, users).
- `src/tasks/` Celery tasks (autodiscovered).
- `src/tests/` app tests.
- `src/modules/users/fixtures/` JSON fixtures (permissions).
- `alembic/` migration scripts and environment.
- `compose/local/` Dockerfile and startup scripts.
- `local.yml` Docker Compose file for local dev.
- `requirements/` pip requirements per environment.

## Local venv for LSP support
Create a local virtual environment so your editor can index packages and
provide autocomplete/diagnostics:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements/local/requirements.txt
```

Point your editor's Python interpreter to `.venv/bin/python` (for example,
in VS Code: Command Palette -> "Python: Select Interpreter").

## Dockerfile and local.yml
Dockerfile (`compose/local/Dockerfile`):
- Builds a Python 3.12 Alpine image.
- Installs `requirements/local/requirements.txt`.
- Copies the app into `/app`.
- Installs the `/start-celery` script used by the worker container.

Compose file (`local.yml`):
- `postgres` service for Postgres 16.
- `api` service builds the Dockerfile, mounts the repo, loads `.envs/local/*`,
  exposes port 8000, and runs `fastapi run src/main.py`.
- `redis` service for Celery broker/backend.
- `worker` service reuses the api image and runs `/start-celery`.

## Env example
Compose loads three env files:
- `.envs/local/.vars`
- `.envs/local/.db`
- `.envs/local/.cloud`

Example content (split as you prefer across those files):

```env
ENV=local
DATABASE_URL=postgresql+psycopg2://postgres:postgres@postgres:5432/postgres
REDIS_URL=redis://redis:6379
SECRET_KEY=replace-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
# Optional: used by `make admin` to create/update an admin user.
ADMIN_EMAIL=admin@example.com
# Leave empty in versioned env files; provide at runtime.
ADMIN_PASSWORD=
# Comma-separated roles; defaults to superadmin in the CLI if omitted.
ADMIN_ROLES=superadmin
MAIL_USERNAME=your-user
MAIL_PASSWORD=your-pass
MAIL_FROM=your-email@example.com
MAIL_PORT=465
MAIL_SERVER=smtp.example.com
MAIL_STARTTLS=False
MAIL_SSL_TLS=True
MAIL_USE_CREDENTIALS=True
MAIL_VALIDATE_CERTS=True
```

## Settings structure
`src/settings.py` defines:
- `environment` (`ENV`)
- `database_url` (`DATABASE_URL`)
- `redis_url` (`REDIS_URL`)
- `secret_key` (`SECRET_KEY`)
- `algorithm` (`ALGORITHM`)
- `access_token_expire_minutes` (`ACCESS_TOKEN_EXPIRE_MINUTES`)
- `mail_conf` (nested mail config using the `MAIL_*` vars)

## Start a local container with make up
Run:
```bash
make up
```

## Tests
- Keep all tests under `src/tests/`.
- Run the test suite via the Makefile:

```bash
make test
```

## Database configuration and migrations (Alembic + Makefile)
- Runtime DB connection is created from `settings.database_url`
  in `src/core/database.py`.
- The app calls `create_db_and_tables()` on startup to create tables.
- Alembic is configured in `alembic/env.py` and uses `settings.database_url`,
  so it targets the same Postgres instance as the app.
- Migrations live in `alembic/versions/`.
- User emails are unique (see latest migration).

Makefile commands:
- `make mm msg="your message"` generates a revision (autogenerate).
- `make m` applies migrations (`alembic upgrade head`).

## Authentication, authorization, roles, and permissions
- Authentication uses OAuth2 password flow (`/v1/auth/login`) and JWTs.
- Passwords are hashed with `pwdlib` in `src/core/authentication.py`.
- Roles are `user`, `admin`, `superadmin` (see `src/modules/users/enums.py`).
- Authorization is role-then-permission based:
  `require_role(...)` checks explicit roles first, then permission fixtures.
- Permissions map route names to roles in
  `src/modules/users/fixtures/permissions.json`.
- Fixtures are loaded with `src/core/load_fixtures.py` (manual run).

## How to use or secure an endpoint
Using a protected endpoint:
- Get a token by posting credentials to `/v1/auth/login`.
- Send `Authorization: Bearer <access_token>` with the request.
- Ensure the user has a role whose permissions include the route name.

Securing a new endpoint:
- Add the route under `src/modules/` and give it a stable route name.
- Require authentication via the shared dependency used in routes.
- Add the route name to the appropriate role list in
  `src/modules/users/fixtures/permissions.json`.
- Run `python -m src.core.load_fixtures` to refresh permissions.

## Auth and users endpoints
- `POST /v1/auth/login` issues a JWT.
- `POST /v1/auth/signup` creates a user (default role: `user`).
- `GET /v1/users` lists users (superadmin).
- `GET /v1/users/me` returns the current user.
- `POST /v1/users/{id}` fetches a user by id (superadmin).
- `PATCH /v1/users/{id}` updates a user.
- `DELETE /v1/users/{id}` deletes a user (superadmin).

## Celery configuration
- Celery is configured in `src/core/celery.py` with Redis as broker/backend.
- The worker is started by `compose/local/commands/start-celery`.
- Tasks are autodiscovered from `src/tasks`, and all tasks must live under
  the `tasks/` folder.

## Email configuration
- Email settings come from `MAIL_*` env vars in `src/settings.py`.
- `src/core/mail.py` uses fastapi-mail with SMTP in `prod`,
  and a console sender in other environments.
