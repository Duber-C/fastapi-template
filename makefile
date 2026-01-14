DOCKER_COMPOSE_FILE = local.yml

up:
	docker compose -f $(DOCKER_COMPOSE_FILE) up

down:
	docker compose -f $(DOCKER_COMPOSE_FILE) down

build:
	docker compose -f $(DOCKER_COMPOSE_FILE) build

test:
	docker compose -f $(DOCKER_COMPOSE_FILE) run --rm api pytest
