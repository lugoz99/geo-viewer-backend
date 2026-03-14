.PHONY: up down build logs logs-db restart shell db-shell migrate migrate-down migration local-db local-run local-migration local-migrate local-migrate-down local-migrate-reset clean clean-all

include .env
export

# ─── Docker: Levantar/Bajar ───────────────────────────────────
up:
	docker compose --env-file .env.docker up -d

build:
	docker compose --env-file .env.docker up -d --build

down:
	docker compose down

# ─── Docker: Logs ─────────────────────────────────────────────
logs:
	docker compose logs -f api

logs-db:
	docker compose logs -f db

# ─── Docker: Utilidades ───────────────────────────────────────
restart:
	docker compose restart api

shell:
	docker compose exec api bash

db-shell:
	docker compose exec db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}

# ─── Docker: Migraciones ──────────────────────────────────────
migration:
	docker compose exec api uv run alembic revision --autogenerate -m "$(name)"

migrate:
	docker compose exec api uv run alembic upgrade head

migrate-down:
	docker compose exec api uv run alembic downgrade -1

# ─── Local: Desarrollo ────────────────────────────────────────
local-db:
	docker compose up db -d

local-run: local-db
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

local-migration: local-db
	uv run alembic revision --autogenerate -m "$(name)"

local-migrate: local-db
	uv run alembic upgrade head

local-migrate-down:
	uv run alembic downgrade -1

local-migrate-reset:
	uv run alembic downgrade base

# ─── Limpieza ─────────────────────────────────────────────────
clean:
	docker compose down

clean-all:
	docker compose down -v