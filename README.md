# FastAPI Example

## Stack
- FastAPI for the API layer.
- SQLModel for ORM models and database access.
- Alembic for migrations.
- PostgreSQL (default in settings/compose) and SQLite for local Alembic config.
- Redis + Celery for background tasks.
- fastapi-mail for email delivery.
- Docker and Docker Compose for local services.

## Repo structure
- `src/` application code (routes, internal models, utils, tasks).
- `src/routes/` FastAPI routers and endpoints.
- `src/internal/` SQLModel models and domain logic.
- `src/utils/` shared helpers (auth, database, mail, celery, fixtures).
- `src/tasks/` Celery tasks (autodiscovered).
- `src/fixtures/` JSON fixtures
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
- Keep all tests under `tests/`.
- Run the test suite via the Makefile:

```bash
make test
```

## Database configuration and migrations (Alembic + Makefile)
- Runtime DB connection is created from `settings.database_url`
  in `src/utils/database.py`.
- The app calls `create_db_and_tables()` on startup to create tables.
- Alembic is configured in `alembic/env.py` and uses `settings.database_url`,
  so it targets the same Postgres instance as the app.
- Migrations live in `alembic/versions/`.

Makefile commands:
- `make mm msg="your message"` generates a revision (autogenerate).
- `make m` applies migrations (`alembic upgrade head`).

## Authentication, authorization, roles, and permissions
- Authentication uses OAuth2 password flow (`/auth/token`) and JWTs.
- Passwords are hashed with `pwdlib` in `src/utils/authentication.py`.
- Authorization is permission-based: each request checks if the current
  route name matches a permission assigned to one of the user's roles.
- Role/permission fixtures live in `src/fixtures/*.json` and are loaded
  on startup by `src/utils/load_fixtures.py`.
- If you add routes or change permission names, update the fixtures
  accordingly so access rules stay in sync.

## Celery configuration
- Celery is configured in `src/utils/celery.py` with Redis as broker/backend.
- The worker is started by `compose/local/commands/start-celery`.
- Tasks are autodiscovered from `src/tasks`, and all tasks must live under
  the `tasks/` folder.

## Email configuration
- Email settings come from `MAIL_*` env vars in `src/settings.py`.
- `src/utils/mail.py` uses fastapi-mail with SMTP in `prod`,
  and a console sender in other environments.
