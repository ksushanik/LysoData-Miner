# LysoData-Miner Main Makefile
# Consolidated project management

.DEFAULT_GOAL := help

# Colors
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
CYAN := \033[36m
RESET := \033[0m

help: ## Show this help message
	@echo "$(BLUE)🧬 LysoData-Miner Project Management$(RESET)"
	@echo "$(BLUE)==================================$(RESET)"
	@echo ""
	@echo "$(GREEN)📋 Main Commands:$(RESET)"
	@echo "  $(CYAN)make dev-setup$(RESET)           # Setup development environment"
	@echo "  $(CYAN)make dev-start$(RESET)           # Start development servers"
	@echo "  $(CYAN)make dev-stop$(RESET)            # Stop development servers"
	@echo "  $(CYAN)make deploy$(RESET)              # Deploy to production (4feb)"
	@echo ""
	@echo "$(GREEN)🚀 CI/CD Commands:$(RESET)"
	@echo "  $(CYAN)make cicd-help$(RESET)           # Show CI/CD commands"
	@echo "  $(CYAN)make cicd-deploy$(RESET)         # Deploy using CI/CD system"
	@echo "  $(CYAN)make cicd-status$(RESET)         # Show CI/CD system status"
	@echo ""
	@echo "$(GREEN)📚 Documentation:$(RESET)"
	@echo "  📖 Project structure: $(YELLOW)PROJECT_STRUCTURE.md$(RESET)"
	@echo "  📖 Quick start guide: $(YELLOW)docs/deployment/CI_CD_QUICK_START.md$(RESET)"
	@echo "  📖 Full CI/CD guide: $(YELLOW)docs/deployment/CI_CD_GUIDE.md$(RESET)"
	@echo ""
	@echo "$(GREEN)🔧 Specialized Makefiles:$(RESET)"
	@echo "  $(CYAN)make -f config/makefiles/Makefile.development$(RESET) [command]"
	@echo "  $(CYAN)make -f config/makefiles/Makefile.production$(RESET) [command]"
	@echo "  $(CYAN)make -f config/makefiles/Makefile.cicd$(RESET) [command]"

dev-setup: ## Setup development environment
	@echo "$(BLUE)🔧 Setting up development environment...$(RESET)"
	@echo "$(CYAN)📋 Creating necessary directories...$(RESET)"
	@mkdir -p logs backups/database
	@echo "$(CYAN)📋 Making scripts executable...$(RESET)"
	@chmod +x scripts/deployment/*.sh scripts/deployment/*.py
	@echo "$(CYAN)📋 Checking Docker...$(RESET)"
	@docker info >/dev/null 2>&1 && echo "$(GREEN)✅ Docker is running$(RESET)" || echo "$(RED)❌ Docker is not running$(RESET)"
	@echo "$(GREEN)✅ Development environment setup complete!$(RESET)"
	@echo ""
	@echo "$(YELLOW)💡 Next steps:$(RESET)"
	@echo "  1. Copy and configure: cp config/environment/env.example .env"
	@echo "  2. Start development: make dev-start"

dev-start: ## Start development servers
	@echo "$(BLUE)🚀 Starting development servers...$(RESET)"
	@docker-compose -f config/docker/docker-compose.yml up -d
	@echo "$(GREEN)✅ Development servers started!$(RESET)"
	@echo "$(CYAN)Frontend: http://localhost:3000$(RESET)"
	@echo "$(CYAN)Backend: http://localhost:8000$(RESET)"

dev-stop: ## Stop development servers
	@echo "$(BLUE)🛑 Stopping development servers...$(RESET)"
	@docker-compose -f config/docker/docker-compose.yml down
	@echo "$(GREEN)✅ Development servers stopped!$(RESET)"

deploy: ## Deploy to production (4feb server)
	@echo "$(BLUE)🚀 Deploying to production...$(RESET)"
	@make -f config/makefiles/Makefile.cicd deploy

# CI/CD Commands (delegated to specialized makefile)
cicd-help: ## Show CI/CD commands
	@make -f config/makefiles/Makefile.cicd help

cicd-deploy: ## Deploy using CI/CD system
	@make -f config/makefiles/Makefile.cicd deploy

cicd-status: ## Show CI/CD system status
	@make -f config/makefiles/Makefile.cicd cicd-status

cicd-setup: ## Setup CI/CD system
	@make -f config/makefiles/Makefile.cicd cicd-setup

# Project status
status: ## Show project status
	@echo "$(BLUE)📊 LysoData-Miner Project Status$(RESET)"
	@echo "$(BLUE)===============================$(RESET)"
	@echo ""
	@echo "$(GREEN)🔧 System Components:$(RESET)"
	@echo -n "  Docker: "
	@docker info >/dev/null 2>&1 && echo "$(GREEN)✅ Running$(RESET)" || echo "$(RED)❌ Not running$(RESET)"
	@echo -n "  Git: "
	@git status >/dev/null 2>&1 && echo "$(GREEN)✅ Repository OK$(RESET)" || echo "$(RED)❌ Not a git repository$(RESET)"
	@echo ""
	@echo "$(GREEN)📁 Project Structure:$(RESET)"
	@echo "  📚 Documentation: $(shell find docs -name "*.md" | wc -l) files"
	@echo "  🚀 Scripts: $(shell find scripts -name "*.sh" -o -name "*.py" | wc -l) files"
	@echo "  ⚙️ Config files: $(shell find config -name "*.yml" -o -name "*.example" | wc -l) files"
	@echo "  💾 Backups: $(shell find backups -name "*" -type f 2>/dev/null | wc -l) files"

clean: ## Clean temporary files
	@echo "$(BLUE)🧹 Cleaning temporary files...$(RESET)"
	@rm -f *.log *.pid .last_*
	@rm -rf __pycache__ .pytest_cache
	@echo "$(GREEN)✅ Temporary files cleaned!$(RESET)"

.PHONY: help dev-setup dev-start dev-stop deploy cicd-help cicd-deploy cicd-status cicd-setup status clean
