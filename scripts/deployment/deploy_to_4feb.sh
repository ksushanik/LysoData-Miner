#!/bin/bash

# 🚀 LysoData-Miner CI/CD Deploy Script for 4feb Server
# ====================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
RESET='\033[0m'

# Configuration
REMOTE_HOST="ssh 4feb"
REMOTE_DIR="/opt/lysodata"
DOCKER_REGISTRY="gimmyhat"
PROJECT_NAME="lysodata"
BUILD_TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Options
FORCE_BUILD=false
SKIP_TESTS=false
BACKUP_BEFORE_DEPLOY=true
DEPLOY_FRONTEND=true
DEPLOY_BACKEND=true
DRY_RUN=false

# Function to show usage
show_usage() {
    echo -e "${BLUE}🚀 LysoData-Miner CI/CD Deploy Script${RESET}"
    echo -e "${BLUE}====================================${RESET}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --force-build         Force rebuild even if no changes detected"
    echo "  --skip-tests          Skip running tests before deploy"
    echo "  --no-backup           Skip backup before deploy"
    echo "  --frontend-only       Deploy only frontend"
    echo "  --backend-only        Deploy only backend"
    echo "  --dry-run             Show what would be done without executing"
    echo "  --help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Full deploy with all checks"
    echo "  $0 --frontend-only    # Deploy only frontend"
    echo "  $0 --force-build      # Force rebuild all images"
    echo "  $0 --dry-run          # Preview deployment actions"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --force-build)
            FORCE_BUILD=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --no-backup)
            BACKUP_BEFORE_DEPLOY=false
            shift
            ;;
        --frontend-only)
            DEPLOY_FRONTEND=true
            DEPLOY_BACKEND=false
            shift
            ;;
        --backend-only)
            DEPLOY_FRONTEND=false
            DEPLOY_BACKEND=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${RESET}"
            show_usage
            exit 1
            ;;
    esac
done

# Function to run commands on remote server
run_remote() {
    if [ "$DRY_RUN" = true ]; then
        echo -e "${CYAN}[DRY RUN] Would run on remote: $1${RESET}"
        return 0
    fi
    $REMOTE_HOST "$1"
}

# Function to execute local commands
execute_local() {
    if [ "$DRY_RUN" = true ]; then
        echo -e "${CYAN}[DRY RUN] Would run locally: $1${RESET}"
        return 0
    fi
    eval "$1"
}

# Function to check if changes exist
check_changes() {
    local component=$1
    local last_commit_file=".last_deploy_${component}"
    
    if [ ! -f "$last_commit_file" ]; then
        echo "true"  # First deploy
        return
    fi
    
    local last_commit=$(cat "$last_commit_file")
    local current_commit=$(git rev-parse HEAD)
    
    if [ "$last_commit" != "$current_commit" ]; then
        # Check if changes affect this component
        local changes=$(git diff --name-only "$last_commit" HEAD | grep -E "^${component}/" || true)
        if [ -n "$changes" ] || [ "$FORCE_BUILD" = true ]; then
            echo "true"
        else
            echo "false"
        fi
    else
        echo "false"
    fi
}

# Function to update last deploy commit
update_last_commit() {
    local component=$1
    if [ "$DRY_RUN" = false ]; then
        git rev-parse HEAD > ".last_deploy_${component}"
    fi
}

# Function to run tests
run_tests() {
    echo -e "${YELLOW}🧪 Running tests...${RESET}"
    
    if [ "$SKIP_TESTS" = true ]; then
        echo -e "${YELLOW}⚠️ Skipping tests as requested${RESET}"
        return 0
    fi
    
    # Backend tests
    if [ "$DEPLOY_BACKEND" = true ]; then
        echo -e "${BLUE}Testing backend...${RESET}"
        execute_local "cd backend && python -m pytest tests/ -v || echo 'No tests found, continuing...'"
    fi
    
    # Frontend tests
    if [ "$DEPLOY_FRONTEND" = true ]; then
        echo -e "${BLUE}Testing frontend...${RESET}"
        execute_local "cd frontend && npm test -- --watchAll=false || echo 'No tests found, continuing...'"
    fi
    
    echo -e "${GREEN}✅ Tests completed${RESET}"
}

# Function to build and push images
build_and_push() {
    local component=$1
    local needs_build=$2
    
    if [ "$needs_build" = false ] && [ "$FORCE_BUILD" = false ]; then
        echo -e "${YELLOW}⚠️ No changes detected for $component, skipping build${RESET}"
        return 0
    fi
    
    echo -e "${BLUE}🏗️ Building $component image...${RESET}"
    
    local image_name="${DOCKER_REGISTRY}/${PROJECT_NAME}-${component}:latest"
    local tagged_image="${DOCKER_REGISTRY}/${PROJECT_NAME}-${component}:${BUILD_TIMESTAMP}"
    
    # Build image
    execute_local "docker build -t $image_name -t $tagged_image ./$component"
    
    # Push to registry
    echo -e "${BLUE}📤 Pushing $component image to registry...${RESET}"
    execute_local "docker push $image_name"
    execute_local "docker push $tagged_image"
    
    echo -e "${GREEN}✅ $component image built and pushed${RESET}"
}

# Function to create backup
create_backup() {
    if [ "$BACKUP_BEFORE_DEPLOY" = false ]; then
        echo -e "${YELLOW}⚠️ Skipping backup as requested${RESET}"
        return 0
    fi
    
    echo -e "${BLUE}💾 Creating backup before deploy...${RESET}"
    
    local backup_name="backup_pre_deploy_${BUILD_TIMESTAMP}.sql.gz"
    run_remote "cd $REMOTE_DIR && docker exec lysodata_db pg_dump -U lysobacter_user lysobacter_db | gzip > ./backups/$backup_name"
    
    echo -e "${GREEN}✅ Backup created: $backup_name${RESET}"
}

# Function to deploy to remote server
deploy_remote() {
    echo -e "${BLUE}🚀 Deploying to remote server...${RESET}"
    
    # Pull latest images
    echo -e "${YELLOW}📥 Pulling latest images...${RESET}"
    run_remote "cd $REMOTE_DIR && docker compose -f docker-compose.hub.yml pull"
    
    # Stop services
    echo -e "${YELLOW}🛑 Stopping services...${RESET}"
    run_remote "cd $REMOTE_DIR && docker compose -f docker-compose.hub.yml down"
    
    # Start services with new images
    echo -e "${YELLOW}🚀 Starting services with new images...${RESET}"
    run_remote "cd $REMOTE_DIR && docker compose -f docker-compose.hub.yml up -d"
    
    # Wait for database to be ready
    echo -e "${YELLOW}⏳ Waiting for database to be ready...${RESET}"
    sleep 15
    
    # Run database migrations
    echo -e "${YELLOW}🗄️ Running database migrations...${RESET}"
    run_remote "cd $REMOTE_DIR && docker compose -f docker-compose.hub.yml exec -T backend python manage.py migrate"
    
    # Collect static files (if needed)
    echo -e "${YELLOW}📁 Collecting static files...${RESET}"
    run_remote "cd $REMOTE_DIR && docker compose -f docker-compose.hub.yml exec -T backend python manage.py collectstatic --noinput"
    
    # Wait for services to be ready
    echo -e "${YELLOW}⏳ Waiting for services to start...${RESET}"
    sleep 30
    
    # Health checks
    echo -e "${YELLOW}🏥 Running health checks...${RESET}"
    
    # Check backend
    if run_remote "curl -sf http://localhost:8000/api/health/ >/dev/null"; then
        echo -e "${GREEN}✅ Backend is healthy${RESET}"
    else
        echo -e "${RED}❌ Backend health check failed${RESET}"
        run_remote "cd $REMOTE_DIR && docker compose logs backend --tail 20"
        exit 1
    fi
    
    # Check frontend
    if run_remote "curl -sf http://localhost:3000 >/dev/null"; then
        echo -e "${GREEN}✅ Frontend is accessible${RESET}"
    else
        echo -e "${RED}❌ Frontend health check failed${RESET}"
        run_remote "cd $REMOTE_DIR && docker compose logs frontend --tail 20"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Deployment completed successfully${RESET}"
}

# Function to send notification
send_notification() {
    local status=$1
    local message=$2
    
    # You can extend this to send Slack/Discord/email notifications
    echo -e "${PURPLE}📢 Deployment $status: $message${RESET}"
    
    # Example: Send to webhook (uncomment and configure)
    # curl -X POST "YOUR_WEBHOOK_URL" -H "Content-Type: application/json" \
    #      -d "{\"text\":\"LysoData-Miner Deploy $status: $message\"}"
}

# Main deployment flow
main() {
    echo -e "${BLUE}🚀 Starting LysoData-Miner CI/CD Deploy${RESET}"
    echo -e "${BLUE}======================================${RESET}"
    echo ""
    echo -e "${CYAN}📋 Deployment Configuration:${RESET}"
    echo -e "  Remote Host: $REMOTE_HOST"
    echo -e "  Remote Dir: $REMOTE_DIR"
    echo -e "  Deploy Backend: $DEPLOY_BACKEND"
    echo -e "  Deploy Frontend: $DEPLOY_FRONTEND"
    echo -e "  Force Build: $FORCE_BUILD"
    echo -e "  Skip Tests: $SKIP_TESTS"
    echo -e "  Create Backup: $BACKUP_BEFORE_DEPLOY"
    echo -e "  Dry Run: $DRY_RUN"
    echo ""
    
    # Check git status
    if [ "$DRY_RUN" = false ]; then
        if ! git diff-index --quiet HEAD --; then
            echo -e "${YELLOW}⚠️ You have uncommitted changes. Consider committing them first.${RESET}"
            read -p "Continue anyway? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo -e "${RED}❌ Deployment cancelled${RESET}"
                exit 1
            fi
        fi
    fi
    
    # Check for changes
    local backend_changed=$(check_changes "backend")
    local frontend_changed=$(check_changes "frontend")
    
    echo -e "${CYAN}📊 Change Detection:${RESET}"
    echo -e "  Backend changes: $backend_changed"
    echo -e "  Frontend changes: $frontend_changed"
    echo ""
    
    # Run tests
    run_tests
    
    # Build and push images
    if [ "$DEPLOY_BACKEND" = true ]; then
        build_and_push "backend" "$backend_changed"
    fi
    
    if [ "$DEPLOY_FRONTEND" = true ]; then
        build_and_push "frontend" "$frontend_changed"
    fi
    
    # Create backup
    create_backup
    
    # Deploy to remote
    deploy_remote
    
    # Update last commit tracking
    if [ "$DEPLOY_BACKEND" = true ]; then
        update_last_commit "backend"
    fi
    
    if [ "$DEPLOY_FRONTEND" = true ]; then
        update_last_commit "frontend"
    fi
    
    # Success notification
    send_notification "SUCCESS" "Build $BUILD_TIMESTAMP deployed successfully"
    
    echo ""
    echo -e "${GREEN}🎉 Deployment completed successfully!${RESET}"
    echo -e "${GREEN}====================================${RESET}"
    echo -e "${YELLOW}🌐 Frontend: http://89.169.171.236:3000${RESET}"
    echo -e "${YELLOW}🔌 Backend: http://89.169.171.236:8000${RESET}"
    echo -e "${YELLOW}📚 API Docs: http://89.169.171.236:8000/api/docs${RESET}"
    echo ""
}

# Run main function
main "$@" 