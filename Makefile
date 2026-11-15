.PHONY: help install up down logs ps db-generate migrate dev test lint

help:
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "%-14s %s\n", $$1, $$2}'

install: ## Install Node workspace dependencies
	npm install

up: ## Start local infrastructure
	docker compose -f infra/compose/docker-compose.yml up -d

down: ## Stop local infrastructure
	docker compose -f infra/compose/docker-compose.yml down

logs: ## Tail infrastructure logs
	docker compose -f infra/compose/docker-compose.yml logs -f --tail=100

ps: ## Show infrastructure status
	docker compose -f infra/compose/docker-compose.yml ps

db-generate: ## Generate the Prisma client
	npm run db:generate

migrate: ## Apply Prisma migrations
	npm run db:migrate

dev: ## Run web and api in watch mode
	npm run dev

test: ## Run JS unit tests
	npm test

lint: ## Lint web and api
	npm run lint
