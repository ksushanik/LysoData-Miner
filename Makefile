# LysoData-Miner Development Makefile
# ===================================
# Commands for managing the full-stack Lysobacter identification system

.PHONY: help install dev build test clean docker-build docker-up docker-down logs

# Colors for better readability
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Default target
help: ## Show this help message
	@echo "$(BLUE)🧬 LysoData-Miner Development Commands$(RESET)"
	@echo "$(BLUE)=====================================$(RESET)"
	@echo ""
	@echo "$(GREEN)Quick Start:$(RESET)"
	@echo "  make install    # Install all dependencies"
	@echo "  make dev        # Start development servers"
	@echo "  make stop       # Stop development servers"
	@echo "  make build      # Build for production"
	@echo "  make clean      # Clean build artifacts"
	@echo "  make validate-json JSON_FILE=file.json  # Validate JSON structure"
	@echo "  make import-json   JSON_FILE=file.json  # Import JSON into database"
	@echo ""
	@echo "$(GREEN)Available commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  $(YELLOW)%-15s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# Installation targets
install: install-backend install-frontend ## Install all dependencies
	@echo "$(GREEN)✅ All dependencies installed successfully!$(RESET)"

install-backend: ## Install Python backend dependencies
	@echo "$(BLUE)📦 Installing backend dependencies...$(RESET)"
	cd backend && python3 -m pip install --upgrade pip
	cd backend && python3 -m pip install -r requirements.txt
	@echo "$(GREEN)✅ Backend dependencies installed$(RESET)"

install-frontend: ## Install Node.js frontend dependencies
	@echo "$(BLUE)📦 Installing frontend dependencies...$(RESET)"
	cd frontend && npm install
	@echo "$(GREEN)✅ Frontend dependencies installed$(RESET)"

# Development targets
dev: ## Start development servers (backend + frontend)
	@echo "$(BLUE)🚀 Starting development environment...$(RESET)"
	@echo "$(YELLOW)Backend will be available at: http://localhost:8000$(RESET)"
	@echo "$(YELLOW)Frontend will be available at: http://localhost:3000$(RESET)"
	@echo "$(YELLOW)API docs will be available at: http://localhost:8000/docs$(RESET)"
	@echo ""
	@$(MAKE) -j2 dev-backend dev-frontend

dev-backend: ## Start FastAPI backend server
	@echo "$(BLUE)🧬 Starting backend server...$(RESET)"
	cd backend && python3 run_server.py

dev-frontend: ## Start React frontend development server
	@echo "$(BLUE)⚛️  Starting frontend development server...$(RESET)"
	cd frontend && npm run dev

# Build targets
build: build-backend build-frontend ## Build both backend and frontend

build-backend: ## Build backend Docker image
	@echo "$(BLUE)🐳 Building backend Docker image...$(RESET)"
	docker build -t lysodata-miner-backend ./backend
	@echo "$(GREEN)✅ Backend image built$(RESET)"

build-frontend: ## Build frontend for production
	@echo "$(BLUE)🏗️  Building frontend for production...$(RESET)"
	cd frontend && npm run build
	@echo "$(GREEN)✅ Frontend built$(RESET)"

# Testing targets
test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	@echo "$(BLUE)🧪 Running backend tests...$(RESET)"
	cd backend && python3 -m pytest

test-frontend: ## Run frontend tests
	@echo "$(BLUE)🧪 Running frontend tests...$(RESET)"
	cd frontend && npm run test

# Type checking
type-check: ## Check TypeScript types
	@echo "$(BLUE)🔍 Checking TypeScript types...$(RESET)"
	cd frontend && npm run type-check

# Linting
lint: lint-backend lint-frontend ## Run all linters

lint-backend: ## Lint backend Python code
	@echo "$(BLUE)🔍 Linting backend code...$(RESET)"
	cd backend && python3 -m flake8 app/
	cd backend && python3 -m black --check app/

lint-frontend: ## Lint frontend TypeScript code
	@echo "$(BLUE)🔍 Linting frontend code...$(RESET)"
	cd frontend && npm run lint

# Docker targets
docker-up: ## Start all services with Docker Compose
	@echo "$(BLUE)🐳 Starting all services with Docker...$(RESET)"
	docker-compose up -d
	@echo "$(GREEN)✅ All services started$(RESET)"
	@echo "$(YELLOW)Services available at:$(RESET)"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend:  http://localhost:8000"
	@echo "  Database: localhost:5434"

docker-down: ## Stop all Docker services
	@echo "$(BLUE)🛑 Stopping all Docker services...$(RESET)"
	docker-compose down

docker-build: ## Build all Docker images
	@echo "$(BLUE)🏗️  Building all Docker images...$(RESET)"
	docker-compose build

docker-logs: ## Show logs from all services
	docker-compose logs -f

# Health checks
health: ## Check health of all services
	@echo "$(BLUE)🏥 Checking service health...$(RESET)"
	@echo "Backend health:"
	@curl -s http://localhost:8000/api/health/ | python3 -m json.tool || echo "$(RED)❌ Backend not responding$(RESET)"
	@echo ""
	@echo "Frontend health:"
	@curl -s http://localhost:3000 > /dev/null && echo "$(GREEN)✅ Frontend responding$(RESET)" || echo "$(RED)❌ Frontend not responding$(RESET)"

# Database management
db-backup: ## Create database backup
	@echo "$(BLUE)💾 Creating database backup...$(RESET)"
	docker-compose exec postgres pg_dump -U lysobacter_user lysobacter_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ Database backup created$(RESET)"

db-restore: ## Restore database from backup (requires BACKUP_FILE variable)
	@echo "$(BLUE)🔄 Restoring database from backup...$(RESET)"
	@if [ -z "$(BACKUP_FILE)" ]; then echo "$(RED)❌ Please specify BACKUP_FILE variable$(RESET)"; exit 1; fi
	docker-compose exec -T postgres psql -U lysobacter_user -d lysobacter_db < $(BACKUP_FILE)
	@echo "$(GREEN)✅ Database restored$(RESET)"

# JSON data import / validation
validate-json: ## Validate JSON file structure (JSON_FILE=path/to/data.json)
	@if [ -z "$(JSON_FILE)" ]; then echo "$(RED)❌ Please specify JSON_FILE=<file.json>$(RESET)"; exit 1; fi
	@echo "$(BLUE)🔎 Validating JSON structure...$(RESET)"
	python3 database/scripts/import_json.py --json-file $(JSON_FILE) --validate-only --db-port 5434

import-json: ## Import JSON data into database (JSON_FILE=path/to/data.json)
	@if [ -z "$(JSON_FILE)" ]; then echo "$(RED)❌ Please specify JSON_FILE=<file.json>$(RESET)"; exit 1; fi
	@echo "$(BLUE)⬆️  Importing JSON data into database...$(RESET)"
	python3 database/scripts/import_json.py --json-file $(JSON_FILE) --import --db-port 5434
	@echo "$(GREEN)✅ JSON import finished$(RESET)"

# Cleanup targets
clean: ## Clean build artifacts and caches
	@echo "$(BLUE)🧹 Cleaning build artifacts...$(RESET)"
	cd backend && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	cd backend && find . -name "*.pyc" -delete 2>/dev/null || true
	cd frontend && rm -rf dist/ node_modules/.cache/ 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup complete$(RESET)"

clean-docker: ## Remove all Docker containers, images, and volumes
	@echo "$(BLUE)🐳 Cleaning Docker resources...$(RESET)"
	docker-compose down -v --rmi all --remove-orphans
	@echo "$(GREEN)✅ Docker cleanup complete$(RESET)"

# Development utilities
stop: ## Stop all development servers and free ports
	@echo "$(BLUE)🛑 Stopping all development servers...$(RESET)"
	@echo "$(YELLOW)Stopping processes by name...$(RESET)"
	@-pkill -f "vite" 2>/dev/null || true
	@-pkill -f "npm run dev" 2>/dev/null || true
	@-pkill -f "uvicorn.*8000" 2>/dev/null || true
	@-pkill -f "python.*run_server.py" 2>/dev/null || true
	@echo "$(YELLOW)Freeing frontend ports (3000-3010)...$(RESET)"
	@-for port in 3000 3001 3002 3003 3004 3005 3006 3007 3008 3009 3010; do \
		lsof -ti:$$port | xargs -r kill -9 2>/dev/null || true; \
	done
	@echo "$(YELLOW)Freeing backend port 8000...$(RESET)"
	@-lsof -ti:8000 | xargs -r kill -9 2>/dev/null || true
	@echo "$(GREEN)✅ All development servers stopped$(RESET)"
	@echo "$(YELLOW)Development ports are now available$(RESET)"

stop-all: ## Stop all services (development + Docker)
	@echo "$(BLUE)🛑 Stopping ALL services...$(RESET)"
	@$(MAKE) stop
	@$(MAKE) docker-down
	@echo "$(GREEN)✅ All services stopped$(RESET)"

kill-ports: ## Force kill processes on development ports (3000-3010, 8000, 5434)
	@echo "$(BLUE)💀 Force killing processes on development ports...$(RESET)"
	@echo "$(YELLOW)Checking frontend ports (3000-3010)...$(RESET)"
	@for port in 3000 3001 3002 3003 3004 3005 3006 3007 3008 3009 3010; do \
		if lsof -ti:$$port >/dev/null 2>&1; then \
			lsof -ti:$$port | xargs -r kill -9 2>/dev/null && echo "$(GREEN)✅ Port $$port freed$(RESET)"; \
		fi; \
	done
	@echo "$(YELLOW)Checking backend port 8000...$(RESET)"
	@-lsof -ti:8000 | xargs -r kill -9 2>/dev/null && echo "$(GREEN)✅ Port 8000 freed$(RESET)" || echo "$(YELLOW)Port 8000 was already free$(RESET)"
	@echo "$(YELLOW)Checking database port 5434...$(RESET)"
	@-lsof -ti:5434 | xargs -r kill -9 2>/dev/null && echo "$(GREEN)✅ Port 5434 freed$(RESET)" || echo "$(YELLOW)Port 5434 was already free$(RESET)"
	@echo "$(GREEN)✅ All development ports checked and freed if necessary$(RESET)"

format: ## Format code (backend and frontend)
	@echo "$(BLUE)✨ Formatting code...$(RESET)"
	cd backend && python3 -m black app/
	cd frontend && npm run format || true
	@echo "$(GREEN)✅ Code formatted$(RESET)"

logs: ## Show logs from development servers
	@echo "$(BLUE)📋 Showing application logs...$(RESET)"
	docker-compose logs -f backend frontend

# Quick development setup
setup: install db-start ## Complete development setup
	@echo "$(GREEN)🎉 Development environment setup complete!$(RESET)"
	@echo ""
	@echo "$(YELLOW)Next steps:$(RESET)"
	@echo "  1. Run 'make dev' to start development servers"
	@echo "  2. Open http://localhost:3000 for frontend"
	@echo "  3. Open http://localhost:8000/docs for API documentation"
	@echo ""

# Production deployment
deploy: build ## Deploy to production
	@echo "$(BLUE)🚀 Deploying to production...$(RESET)"
	@echo "$(YELLOW)⚠️  Production deployment not yet implemented$(RESET)"
	@echo "$(YELLOW)This would typically involve:$(RESET)"
	@echo "  - Building optimized Docker images"
	@echo "  - Pushing to container registry"
	@echo "  - Updating production environment"

# Information targets
info: ## Show project information
	@echo "$(BLUE)🧬 LysoData-Miner Project Information$(RESET)"
	@echo "$(BLUE)====================================$(RESET)"
	@echo ""
	@echo "$(GREEN)Project:$(RESET) Lysobacter Strain Identification Platform"
	@echo "$(GREEN)Backend:$(RESET) FastAPI + PostgreSQL + SQLAlchemy"
	@echo "$(GREEN)Frontend:$(RESET) React + TypeScript + Vite + Tailwind CSS"
	@echo "$(GREEN)Database:$(RESET) PostgreSQL with scientific schema"
	@echo ""
	@echo "$(GREEN)Key Features:$(RESET)"
	@echo "  • Advanced strain identification algorithms"
	@echo "  • Comprehensive test result analysis"
	@echo "  • Modern scientific user interface"
	@echo "  • REST API with OpenAPI documentation"
	@echo "  • Full-stack TypeScript support"
	@echo ""

status: ## Show current service status
	@echo "$(BLUE)📊 Service Status$(RESET)"
	@echo "$(BLUE)==============$(RESET)"
	@echo ""
	@echo "$(GREEN)Docker containers:$(RESET)"
	@docker-compose ps || echo "$(YELLOW)Docker Compose not running$(RESET)"
	@echo ""
	@echo "$(GREEN)Port usage:$(RESET)"
	@lsof -i :3000 || echo "  Port 3000: Available"
	@lsof -i :8000 || echo "  Port 8000: Available"
	@lsof -i :5434 || echo "  Port 5434: Available"

db-start: ## Start PostgreSQL database container
	@echo "$(BLUE)🗄️  Starting PostgreSQL database...$(RESET)"
	docker-compose up -d postgres
	@echo "$(GREEN)✅ Database started$(RESET)"

db-stop: ## Stop PostgreSQL database container
	@echo "$(BLUE)🛑 Stopping database...$(RESET)"
	docker-compose stop postgres

db-shell: ## Connect to database shell
	@echo "$(BLUE)🐘 Connecting to PostgreSQL...$(RESET)"
	docker-compose exec postgres psql -U lysobacter_user -d lysobacter_db

db-logs: ## Show database logs
	docker-compose logs -f postgres 