.PHONY: up down logs logs-backend restart clean build demo dev

up:
	docker compose up -d

down:
	docker compose down

dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up

logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-frontend:
	docker compose logs -f frontend

restart:
	docker compose restart

clean:
	docker compose down -v

build:
	docker compose build --no-cache

demo:
	@echo "Pre-caching demo data..."
	docker compose up -d
	@sleep 5
	docker compose exec backend python -m scripts.seed_demo
	@echo "Demo ready at http://localhost:3000"
