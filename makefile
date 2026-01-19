DOCKER_COMPOSE_FILE = local.yml

up:
	docker compose -f $(DOCKER_COMPOSE_FILE) up --remove-orphans

down:
	docker compose -f $(DOCKER_COMPOSE_FILE) down

build:
	docker compose -f $(DOCKER_COMPOSE_FILE) build

test:
	docker compose -f $(DOCKER_COMPOSE_FILE) run --rm api pytest

load-fixtures:
	docker compose -f $(DOCKER_COMPOSE_FILE) run --rm api python -m src.core.load_fixtures

update-environment:
	pip install -r ./requirements/requirements.txt

mm:
	docker compose -f $(DOCKER_COMPOSE_FILE) run --rm api alembic revision --autogenerate -m "$(msg)"

m:
	docker compose -f $(DOCKER_COMPOSE_FILE) run --rm api alembic upgrade head

db-init:
	docker compose -f $(DOCKER_COMPOSE_FILE) run --rm api alembic init alembic
