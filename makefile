DOCKER_COMPOSE_FILE = local.yml

up:
	docker compose -f $(DOCKER_COMPOSE_FILE) up

build:
	docker compose -f $(DOCKER_COMPOSE_FILE) build

