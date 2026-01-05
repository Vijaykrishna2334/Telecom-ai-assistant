.PHONY: help install dev build up down logs clean test lint format

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install: ## Install all dependencies
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev: ## Start development environment
	docker-compose -f docker-compose.dev.yml up -d

build: ## Build all containers
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs
	docker-compose logs -f

clean: ## Clean up containers and volumes
	docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf backend/dist backend/build backend/*.egg-info
	rm -rf frontend/dist frontend/build frontend/node_modules

test: ## Run tests
	cd backend && pytest tests/ -v

lint: ## Run linters
	cd backend && black app/ tests/
	cd backend && flake8 app/ tests/
	cd backend && mypy app/
	cd frontend && npm run lint

format: ## Format code
	cd backend && black app/ tests/
	cd backend && isort app/ tests/
	cd frontend && npm run format

init-db: ## Initialize database
	python scripts/init_db.py

seed-knowledge: ## Seed knowledge base
	python scripts/seed_knowledge.py

download-models: ## Download voice models
	bash scripts/download_models.sh
