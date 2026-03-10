.PHONY: up down build logs logs-db restart shell db-shell migrate migrate-down migration clean

include .env
export

# ─── Desarrollo docker ───────────────────────────────────────────────

up:
	docker compose up -d

build:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f api

logs-db:
	docker compose logs -f db

restart:
	docker compose restart api

# ─── Desarrollo Local ─────────────────────────────────────────

local-db:
	docker compose up db -d

local-run:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

local-migrate:
	uv run alembic upgrade head

local-migration:
	uv run alembic revision --autogenerate -m "$(name)"

# ─── Acceso a contenedores ────────────────────────────────────

shell:
	docker compose exec api bash

db-shell:
	docker compose exec db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}

# ─── Base de datos ────────────────────────────────────────────

migrate:
	docker compose exec api uv run alembic upgrade head

migrate-down:
	docker compose exec api uv run alembic downgrade -1

migration:
	docker compose exec api uv run alembic revision --autogenerate -m "$(name)"

# ─── Limpieza ─────────────────────────────────────────────────

clean:
	docker compose down -v