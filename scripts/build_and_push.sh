#!/bin/bash

# 🐳 Build and Push LysoData-Miner Images to Docker Hub
# 
# Этот скрипт собирает Docker образы и публикует их на Docker Hub
# под аккаунтом gimmyhat

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Конфигурация
DOCKER_HUB_USER="gimmyhat"
BACKEND_IMAGE="lysodata-backend"
FRONTEND_IMAGE="lysodata-frontend"
VERSION=${1:-latest}

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

# Проверка зависимостей
check_dependencies() {
    print_step "Проверка зависимостей..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker не установлен!"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker daemon не запущен!"
        exit 1
    fi
    
    print_success "Все зависимости установлены"
}

# Проверка авторизации в Docker Hub
check_docker_login() {
    print_step "Проверка авторизации в Docker Hub..."
    
    if ! docker info | grep -q "Username: $DOCKER_HUB_USER"; then
        print_warning "Не авторизован в Docker Hub"
        print_step "Выполняем авторизацию..."
        docker login
    fi
    
    print_success "Авторизация в Docker Hub успешна"
}

# Сборка backend образа
build_backend() {
    print_step "Сборка backend образа..."
    
    cd backend
    
    # Проверяем наличие Dockerfile
    if [ ! -f "Dockerfile" ]; then
        print_error "backend/Dockerfile не найден!"
        exit 1
    fi
    
    # Собираем образ
    docker build \
        -t "$DOCKER_HUB_USER/$BACKEND_IMAGE:$VERSION" \
        -t "$DOCKER_HUB_USER/$BACKEND_IMAGE:latest" \
        .
    
    cd ..
    print_success "Backend образ собран"
}

# Сборка frontend образа
build_frontend() {
    print_step "Сборка frontend образа..."
    
    cd frontend
    
    # Проверяем наличие Dockerfile
    if [ ! -f "Dockerfile" ]; then
        print_error "frontend/Dockerfile не найден!"
        exit 1
    fi
    
    # Собираем образ
    docker build \
        -t "$DOCKER_HUB_USER/$FRONTEND_IMAGE:$VERSION" \
        -t "$DOCKER_HUB_USER/$FRONTEND_IMAGE:latest" \
        .
    
    cd ..
    print_success "Frontend образ собран"
}

# Публикация образов
push_images() {
    print_step "Публикация образов на Docker Hub..."
    
    # Push backend
    print_step "Публикация backend образа..."
    docker push "$DOCKER_HUB_USER/$BACKEND_IMAGE:$VERSION"
    if [ "$VERSION" != "latest" ]; then
        docker push "$DOCKER_HUB_USER/$BACKEND_IMAGE:latest"
    fi
    
    # Push frontend
    print_step "Публикация frontend образа..."
    docker push "$DOCKER_HUB_USER/$FRONTEND_IMAGE:$VERSION"
    if [ "$VERSION" != "latest" ]; then
        docker push "$DOCKER_HUB_USER/$FRONTEND_IMAGE:latest"
    fi
    
    print_success "Все образы успешно опубликованы"
}

# Показать информацию об образах
show_images_info() {
    print_step "Информация о созданных образах:"
    echo ""
    echo -e "${YELLOW}📦 Backend образ:${NC}"
    echo "   🐳 $DOCKER_HUB_USER/$BACKEND_IMAGE:$VERSION"
    echo "   🐳 $DOCKER_HUB_USER/$BACKEND_IMAGE:latest"
    echo ""
    echo -e "${YELLOW}📦 Frontend образ:${NC}"
    echo "   🐳 $DOCKER_HUB_USER/$FRONTEND_IMAGE:$VERSION"
    echo "   🐳 $DOCKER_HUB_USER/$FRONTEND_IMAGE:latest"
    echo ""
    echo -e "${YELLOW}🚀 Для развертывания используйте:${NC}"
    echo "   docker-compose -f docker-compose.hub.yml up -d"
    echo ""
    echo -e "${YELLOW}🌐 Docker Hub URLs:${NC}"
    echo "   https://hub.docker.com/r/$DOCKER_HUB_USER/$BACKEND_IMAGE"
    echo "   https://hub.docker.com/r/$DOCKER_HUB_USER/$FRONTEND_IMAGE"
}

# Очистка локальных образов (опционально)
cleanup_local() {
    if [ "$2" = "--cleanup" ]; then
        print_step "Очистка локальных образов..."
        docker rmi "$DOCKER_HUB_USER/$BACKEND_IMAGE:$VERSION" 2>/dev/null || true
        docker rmi "$DOCKER_HUB_USER/$FRONTEND_IMAGE:$VERSION" 2>/dev/null || true
        if [ "$VERSION" != "latest" ]; then
            docker rmi "$DOCKER_HUB_USER/$BACKEND_IMAGE:latest" 2>/dev/null || true
            docker rmi "$DOCKER_HUB_USER/$FRONTEND_IMAGE:latest" 2>/dev/null || true
        fi
        print_success "Локальные образы очищены"
    fi
}

# Главная функция
main() {
    echo -e "${BLUE}🐳 LysoData-Miner Docker Hub Publishing Script${NC}"
    echo -e "${BLUE}=============================================${NC}"
    echo ""
    
    if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        echo "Использование: $0 [VERSION] [--cleanup] [--no-push]"
        echo ""
        echo "Параметры:"
        echo "  VERSION   - версия образа (по умолчанию: latest)"
        echo "  --cleanup - удалить локальные образы после публикации"
        echo "  --no-push - только сборка, без публикации на Docker Hub"
        echo ""
        echo "Примеры:"
        echo "  $0                    # Сборка и публикация latest"
        echo "  $0 v1.0.0             # Сборка и публикация v1.0.0"
        echo "  $0 v1.0.0 --cleanup   # С очисткой локальных образов"
        echo "  $0 latest --no-push   # Только локальная сборка"
        exit 0
    fi
    
    print_step "Начало сборки и публикации образов (версия: $VERSION)"
    
    # Проверяем параметры
    NO_PUSH=false
    for arg in "$@"; do
        if [ "$arg" = "--no-push" ]; then
            NO_PUSH=true
            break
        fi
    done
    
    check_dependencies
    
    if [ "$NO_PUSH" = "false" ]; then
        check_docker_login
    fi
    
    build_backend
    build_frontend
    
    if [ "$NO_PUSH" = "false" ]; then
        push_images
    else
        print_step "Пропускаем публикацию (--no-push)"
    fi
    
    show_images_info
    cleanup_local "$@"
    
    echo ""
    print_success "🎉 Процесс завершен успешно!"
    print_step "Образы готовы к использованию в docker-compose.hub.yml"
}

# Запуск скрипта
main "$@" 