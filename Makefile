# ============================================================================
# 🧬 LysoData-Miner – SIMPLE ROOT MAKEFILE
# ----------------------------------------------------------------------------
# Один файл → понятное управление.  Основные группы команд:
#   DEV  – локальная разработка (docker-compose.dev)
#   PROD – продакшн (docker-compose.production)
#   DEPLOY – деплой на удаленный сервер
# ----------------------------------------------------------------------------
#   make help            – эта справка
#   make dev-start       – запустить стек разработки (DB+backend+frontend)
#   make dev-stop        – остановить dev-контейнеры
#   make dev-logs        – логи dev
#   make prod-start      – запустить продакшн-стек
#   make prod-stop       – остановить продакшн-стек
#   make prod-logs       – логи продакшн
#   make deploy          – полный деплой на сервер 4feb
#   make deploy-quick    – быстрый деплой без пересборки
#   make deploy-force    – принудительный деплой с пересборкой
#   make db-backup       – создать резерв базы (prod)
#   make db-restore BACKUP=path.sql.gz – восстановить базу (prod)
# ----------------------------------------------------------------------------
# Подробные Makefile'ы из config/ остаются для продвинутых задач, но не
# импортируются здесь, чтобы не перегружать вывод help.
# ============================================================================

.PHONY: help dev-start dev-stop dev-backend dev-frontend dev-status dev-logs prod-start prod-stop prod-build prod-restart prod-status prod-logs db-backup db-restore dev-env dev-rebuild prod-push deploy deploy-quick deploy-force deploy-advanced deploy-dry deploy-frontend-only deploy-backend-only

#####  Базовые переменные ###################################################
# Используем docker compose (плагин Docker >= 20.10)
DC ?= docker compose

# DEV параметры
DEV_COMPOSE   := config/docker/docker-compose.dev.yml
DEV_ENV       := .env.dev

# PROD параметры
PROD_COMPOSE  := docker-compose.production.yml
PROD_ENV      := .env.production

# Деплой параметры
DOCKER_REGISTRY := gimmyhat
PROJECT_NAME := lysodata
REMOTE_SERVER := 4feb
REMOTE_DIR := /opt/lysodata
BUILD_TAG := $(shell date +%Y%m%d-%H%M%S)

# Цвета
B := \033[34m
G := \033[32m
Y := \033[33m
R := \033[31m
X := \033[0m

##### 📖 HELP ################################################################
help: ## Показать эту справку
	@echo "$${B}🧬 LysoData-Miner – Makefile команды$${X}"
	@echo "$${B}=======================================$${X}\n"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS = ":.*?## "} {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo "\n$${Y}DEV стек:$${X} http://localhost:3000  API → :8000  DB → :5433 (или в .env.dev)"
	@echo "$${Y}PROD стек:$${X} http://localhost:3000  API → :8000  DB → :5434 (или в .env.production)"
	@echo "$${Y}DEPLOY:$${X} Сборка и деплой на сервер 4feb с миграциями"

##### 🗂 DEV env helper #######################################################

dev-env: ## 🔑 Проверить или создать .env.dev
	@if [ ! -f $(DEV_ENV) ]; then \
	  echo "$(Y)⚠️  $(DEV_ENV) не найден, создаю...$(X)"; \
	  if [ -f env.dev.example ]; then cp env.dev.example $(DEV_ENV); else touch $(DEV_ENV); fi; \
	  echo "$(G)✅ $(DEV_ENV) создан. Проверьте параметры!$(X)"; \
	fi

##### 🛠 DEV КОМАНДЫ ##########################################################

dev-start: dev-env ## 🚀 Запустить DEV стек (автоматически останавливает prod)
	@echo "$(Y)ℹ️  Останавливаю продакшн-контейнеры, чтобы освободить порты...$(X)"; \
	$(DC) -f $(PROD_COMPOSE) --env-file $(PROD_ENV) down --remove-orphans || true
	$(DC) -f $(DEV_COMPOSE) --env-file $(DEV_ENV) up -d

dev-backend: dev-env ## 🐍 Запустить/перезапустить backend (DEV)
	$(DC) -f $(DEV_COMPOSE) --env-file $(DEV_ENV) up -d backend

dev-frontend: dev-env ## ⚛️  Запустить/перезапустить frontend (DEV)
	$(DC) -f $(DEV_COMPOSE) --env-file $(DEV_ENV) up -d frontend

dev-stop: dev-env ## 🛑 Остановить DEV стек
	$(DC) -f $(DEV_COMPOSE) --env-file $(DEV_ENV) down

dev-status: dev-env ## 📊 Статус DEV контейнеров
	$(DC) -f $(DEV_COMPOSE) --env-file $(DEV_ENV) ps

dev-logs: dev-env ## 📋 Логи DEV (follow)
	$(DC) -f $(DEV_COMPOSE) --env-file $(DEV_ENV) logs -f

dev-rebuild: dev-env ## ♻️  Полная пересборка DEV образов и перезапуск стека
	@echo "$(Y)🔄 Пересобираю DEV образы и перезапускаю стек...$(X)"
	$(DC) -f $(DEV_COMPOSE) --env-file $(DEV_ENV) down
	$(DC) -f $(DEV_COMPOSE) --env-file $(DEV_ENV) build --no-cache
	$(DC) -f $(DEV_COMPOSE) --env-file $(DEV_ENV) up -d
	@echo "$(G)✅ DEV стек пересобран и запущен.$(X)"

##### 🚀 PROD КОМАНДЫ #########################################################

prod-start: ## 🚀 Запустить PROD стек (с билдом при первом запуске)
	$(DC) -f $(PROD_COMPOSE) --env-file $(PROD_ENV) up -d --build
	@echo "$${G}✅ PROD запущен → Frontend http://localhost:$$(grep -E '^WEB_PORT=' $(PROD_ENV) | cut -d'=' -f2 || echo 3000)$${X}"

prod-stop: ## 🛑 Остановить PROD стек
	$(DC) -f $(PROD_COMPOSE) --env-file $(PROD_ENV) down

prod-build: ## 🏗️  Пересобрать образы PROD
	$(DC) -f $(PROD_COMPOSE) --env-file $(PROD_ENV) build

prod-restart: ## 🔄 Перезапустить PROD стек
	$(MAKE) prod-stop
	$(MAKE) prod-start

prod-status: ## 📊 Статус PROD контейнеров
	$(DC) -f $(PROD_COMPOSE) --env-file $(PROD_ENV) ps

prod-logs: ## 📋 Логи PROD (follow)
	$(DC) -f $(PROD_COMPOSE) --env-file $(PROD_ENV) logs -f

prod-push: ## 🐳 Пересобрать и отправить образы на Docker Hub (используй VERSION=vX.Y.Z)
	@VERSION=${VERSION:-latest} ./scripts/build_and_push.sh $$VERSION

##### 🚀 DEPLOY КОМАНДЫ #######################################################

deploy-build: ## 🏗️  Собрать и загрузить образы в Docker Hub
	@echo "$(B)🏗️  Собираю образы для деплоя...$(X)"
	@echo "$(Y)Backend...$(X)"
	@docker build -t $(DOCKER_REGISTRY)/$(PROJECT_NAME)-backend:latest \
		-t $(DOCKER_REGISTRY)/$(PROJECT_NAME)-backend:$(BUILD_TAG) ./backend
	@echo "$(Y)Frontend...$(X)"
	@docker build -t $(DOCKER_REGISTRY)/$(PROJECT_NAME)-frontend:latest \
		-t $(DOCKER_REGISTRY)/$(PROJECT_NAME)-frontend:$(BUILD_TAG) ./frontend
	@echo "$(B)📤 Загружаю образы в Docker Hub...$(X)"
	@docker push $(DOCKER_REGISTRY)/$(PROJECT_NAME)-backend:latest
	@docker push $(DOCKER_REGISTRY)/$(PROJECT_NAME)-backend:$(BUILD_TAG)
	@docker push $(DOCKER_REGISTRY)/$(PROJECT_NAME)-frontend:latest
	@docker push $(DOCKER_REGISTRY)/$(PROJECT_NAME)-frontend:$(BUILD_TAG)
	@echo "$(G)✅ Образы собраны и загружены$(X)"

deploy-migrate: ## 🗄️  Выполнить миграции на удаленном сервере
	@echo "$(B)🗄️  Выполняю миграции на сервере $(REMOTE_SERVER)...$(X)"
	@ssh $(REMOTE_SERVER) "cd $(REMOTE_DIR) && docker compose exec backend python manage.py migrate"
	@echo "$(G)✅ Миграции выполнены$(X)"

deploy-update: ## 🔄 Обновить контейнеры на удаленном сервере
	@echo "$(B)🔄 Обновляю контейнеры на сервере $(REMOTE_SERVER)...$(X)"
	@ssh $(REMOTE_SERVER) "cd $(REMOTE_DIR) && docker compose pull"
	@ssh $(REMOTE_SERVER) "cd $(REMOTE_DIR) && docker compose up -d --force-recreate"
	@echo "$(G)✅ Контейнеры обновлены$(X)"

deploy-status: ## 📊 Проверить статус на удаленном сервере
	@echo "$(B)📊 Статус сервера $(REMOTE_SERVER):$(X)"
	@ssh $(REMOTE_SERVER) "cd $(REMOTE_DIR) && docker compose ps"
	@echo "$(B)🌐 Проверка API...$(X)"
	@ssh $(REMOTE_SERVER) "curl -s http://localhost:8000/api/health/ || echo 'API недоступен'"

deploy-logs: ## 📋 Показать логи с удаленного сервера
	@echo "$(B)📋 Логи с сервера $(REMOTE_SERVER):$(X)"
	@ssh $(REMOTE_SERVER) "cd $(REMOTE_DIR) && docker compose logs --tail=50"

deploy: ## 🚀 Полный деплой (сборка + миграции + обновление)
	@echo "$(B)🚀 Начинаю полный деплой на сервер $(REMOTE_SERVER)...$(X)"
	@$(MAKE) deploy-build
	@$(MAKE) deploy-migrate
	@$(MAKE) deploy-update
	@$(MAKE) deploy-status
	@echo "$(G)🎉 Деплой завершен успешно!$(X)"

deploy-quick: ## ⚡ Быстрый деплой (только обновление контейнеров)
	@echo "$(B)⚡ Быстрый деплой на сервер $(REMOTE_SERVER)...$(X)"
	@$(MAKE) deploy-update
	@$(MAKE) deploy-status
	@echo "$(G)✅ Быстрый деплой завершен!$(X)"

deploy-force: ## 💪 Принудительный деплой (полная пересборка)
	@echo "$(B)💪 Принудительный деплой на сервер $(REMOTE_SERVER)...$(X)"
	@docker system prune -f
	@$(MAKE) deploy-build
	@ssh $(REMOTE_SERVER) "cd $(REMOTE_DIR) && docker system prune -f"
	@$(MAKE) deploy-migrate
	@$(MAKE) deploy-update
	@$(MAKE) deploy-status
	@echo "$(G)🎉 Принудительный деплой завершен!$(X)"

##### 🚀 ПРОДВИНУТЫЙ CI/CD #######################################################

deploy-advanced: ## 🔧 Продвинутый деплой с тестами и проверками (из CI/CD)
	@make -f config/makefiles/Makefile.cicd deploy

deploy-dry: ## 👁️ Предварительный просмотр деплоя
	@make -f config/makefiles/Makefile.cicd deploy-dry-run

deploy-frontend-only: ## ⚛️ Деплой только frontend
	@make -f config/makefiles/Makefile.cicd deploy-frontend

deploy-backend-only: ## 🐍 Деплой только backend  
	@make -f config/makefiles/Makefile.cicd deploy-backend

##### 💾 Бэкапы ###############################################################

db-backup: ## 💾 Создать backup базы (prod)
	@mkdir -p backups
	@FILE=backups/backup_$$(date +%Y%m%d_%H%M%S).sql.gz; \
	docker exec lysodata_db pg_dump -U lysobacter_user lysobacter_db | gzip > $$FILE && \
	echo "$${G}✅ Бэкап сохранён в $$FILE$${X}"

db-restore: ## ♻️  Восстановить базу (используй BACKUP=файл.sql.gz)
	@if [ -z "$(BACKUP)" ]; then \
		echo "$${R}❌ Укажите BACKUP=/path/to/file.sql.gz$${X}"; exit 1; fi
	@gunzip -c $(BACKUP) | docker exec -i lysodata_db psql -U lysobacter_user -d lysobacter_db
	@echo "$${G}✅ База восстановлена из $(BACKUP)$${X}"
