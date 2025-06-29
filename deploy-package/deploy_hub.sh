#!/bin/bash

# 🚀 Deploy LysoData-Miner from Docker Hub
# 
# Быстрое развертывание системы с использованием готовых образов

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Конфигурация
COMPOSE_FILE="docker-compose.hub.yml"
ENV_FILE=".env"
ENV_EXAMPLE="env.hub.example"

# Функции для вывода
print_step() {
    echo -e "${BLUE}🔄 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Определение команды Docker Compose
get_docker_compose_cmd() {
    if command -v docker-compose &> /dev/null; then
        echo "docker-compose"
    else
        echo "docker compose"
    fi
}

# Проверка зависимостей
check_dependencies() {
    print_step "Проверка зависимостей..."
    
    # Проверка Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker не установлен"
        exit 1
    fi
    
    # Проверка Docker Compose
    if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
        print_error "Docker Compose не установлен"
        exit 1
    fi
    
    # Проверка работы Docker
    if ! docker info &> /dev/null; then
        print_error "Docker не запущен или нет прав доступа"
        exit 1
    fi
    
    print_success "Все зависимости установлены"
}

# Проверка конфигурации
check_config() {
    print_step "Проверка конфигурации..."
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        print_error "Файл $COMPOSE_FILE не найден"
        exit 1
    fi
    
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$ENV_EXAMPLE" ]; then
            print_warning "Файл .env не найден, создаем из примера..."
            cp "$ENV_EXAMPLE" "$ENV_FILE"
            print_warning "⚠️  ВАЖНО: Отредактируйте файл .env перед запуском!"
            print_warning "Особенно измените пароли и порты если нужно"
        else
            print_error "Файл $ENV_FILE не найден и нет примера!"
            exit 1
        fi
    fi
    
    print_success "Конфигурация готова"
}

# Проверка портов
check_ports() {
    print_step "Проверка доступности портов..."
    
    source "$ENV_FILE"
    
    ports_to_check=(
        "${DB_PORT:-5434}"
        "${BACKEND_PORT:-8000}"
        "${WEB_PORT:-3000}"
    )
    
    for port in "${ports_to_check[@]}"; do
        if netstat -tuln 2>/dev/null | grep -q ":$port "; then
            print_warning "Порт $port уже используется"
        fi
    done
    
    print_success "Проверка портов завершена"
}

# Создание директорий
create_directories() {
    print_step "Создание необходимых директорий..."
    
    mkdir -p data/postgres
    mkdir -p data/pgadmin
    mkdir -p backups
    
    print_success "Директории созданы"
}

# Получение образов
pull_images() {
    print_step "Получение образов из Docker Hub..."
    
    source "$ENV_FILE"
    
    docker pull "gimmyhat/lysodata-backend:${BACKEND_VERSION:-latest}"
    docker pull "gimmyhat/lysodata-frontend:${FRONTEND_VERSION:-latest}"
    docker pull "postgres:15-alpine"
    docker pull "dpage/pgadmin4:latest"
    
    print_success "Образы получены"
}

# Запуск сервисов
start_services() {
    print_step "Запуск сервисов..."
    
    DOCKER_COMPOSE=$(get_docker_compose_cmd)
    
    $DOCKER_COMPOSE -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    
    print_success "Сервисы запускаются"
}

# Ожидание готовности сервисов
wait_for_services() {
    print_step "Ожидание готовности сервисов..."
    
    source "$ENV_FILE"
    
    # Ждем backend
    echo -n "Ожидание backend API..."
    for i in {1..30}; do
        if curl -sf "http://localhost:${BACKEND_PORT:-8000}/api/health/" >/dev/null 2>&1; then
            echo -e " ${GREEN}✅${NC}"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    # Ждем frontend
    echo -n "Ожидание frontend..."
    for i in {1..30}; do
        if curl -sf "http://localhost:${WEB_PORT:-3000}" >/dev/null 2>&1; then
            echo -e " ${GREEN}✅${NC}"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    print_success "Сервисы готовы"
}

# Показать статус
show_status() {
    print_step "Статус сервисов:"
    echo ""
    
    source "$ENV_FILE"
    
    DOCKER_COMPOSE=$(get_docker_compose_cmd)
    
    $DOCKER_COMPOSE -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps
    
    echo ""
    echo -e "${GREEN}🌐 Доступные сервисы:${NC}"
    echo "   Frontend:  http://localhost:${WEB_PORT:-3000}"
    echo "   Backend:   http://localhost:${BACKEND_PORT:-8000}"
    echo "   API Docs:  http://localhost:${BACKEND_PORT:-8000}/docs"
    echo "   Database:  localhost:${DB_PORT:-5434}"
    echo "   pgAdmin:   http://localhost:${PGADMIN_PORT:-8080} (опционально)"
    echo ""
    echo -e "${YELLOW}📊 Для просмотра логов:${NC}"
    echo "   $DOCKER_COMPOSE -f $COMPOSE_FILE logs -f"
}

# Показать информацию об образах
show_images_info() {
    print_step "Используемые образы:"
    echo ""
    
    source "$ENV_FILE"
    
    echo -e "${YELLOW}📦 Backend:${NC}  gimmyhat/lysodata-backend:${BACKEND_VERSION:-latest}"
    echo -e "${YELLOW}📦 Frontend:${NC} gimmyhat/lysodata-frontend:${FRONTEND_VERSION:-latest}"
    echo -e "${YELLOW}📦 Database:${NC} postgres:15-alpine"
    echo -e "${YELLOW}📦 Admin:${NC}    dpage/pgadmin4:latest"
}

# Главная функция
main() {
    echo -e "${BLUE}🚀 LysoData-Miner Docker Hub Deployment${NC}"
    echo -e "${BLUE}=======================================${NC}"
    echo ""
    
    if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        echo "Использование: $0 [COMMAND]"
        echo ""
        echo "Команды:"
        echo "  start     - Запустить все сервисы (по умолчанию)"
        echo "  stop      - Остановить все сервисы"
        echo "  restart   - Перезапустить все сервисы"
        echo "  status    - Показать статус сервисов"
        echo "  logs      - Показать логи сервисов"
        echo "  pull      - Обновить образы с Docker Hub"
        echo "  clean     - Остановить и удалить все данные"
        echo ""
        echo "Примеры:"
        echo "  $0                # Запуск сервисов"
        echo "  $0 status         # Проверка статуса"
        echo "  $0 logs           # Просмотр логов"
        exit 0
    fi
    
    DOCKER_COMPOSE=$(get_docker_compose_cmd)
    
    case "${1:-start}" in
        "start")
            check_dependencies
            check_config
            check_ports
            create_directories
            pull_images
            start_services
            wait_for_services
            show_status
            show_images_info
            echo ""
            print_success "🎉 LysoData-Miner успешно развернут!"
            ;;
        "stop")
            print_step "Остановка сервисов..."
            $DOCKER_COMPOSE -f "$COMPOSE_FILE" down
            print_success "Сервисы остановлены"
            ;;
        "restart")
            print_step "Перезапуск сервисов..."
            $DOCKER_COMPOSE -f "$COMPOSE_FILE" down
            sleep 2
            $DOCKER_COMPOSE -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
            print_success "Сервисы перезапущены"
            ;;
        "status")
            show_status
            ;;
        "logs")
            $DOCKER_COMPOSE -f "$COMPOSE_FILE" logs -f
            ;;
        "pull")
            pull_images
            print_success "Образы обновлены"
            ;;
        "clean")
            print_warning "Это удалит все данные! Продолжить? (y/N)"
            read -r response
            if [[ "$response" =~ ^[Yy]$ ]]; then
                $DOCKER_COMPOSE -f "$COMPOSE_FILE" down -v --rmi all
                rm -rf data/ backups/
                print_success "Очистка завершена"
            else
                print_step "Операция отменена"
            fi
            ;;
        *)
            print_error "Неизвестная команда: $1"
            print_step "Используйте $0 --help для справки"
            exit 1
            ;;
    esac
}

# Запуск скрипта
main "$@" 