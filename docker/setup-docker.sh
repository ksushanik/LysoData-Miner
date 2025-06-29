#!/bin/bash

# Docker Setup Script for Lysobacter Database
# Sets up and manages PostgreSQL container for the project

set -e  # Exit on any error

# Configuration
CONTAINER_NAME="lysobacter_postgres"
DB_PORT="5433"
DB_NAME="lysobacter_db"
DB_USER="lysobacter_user"
DB_PASSWORD="lysobacter_password"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed and running
check_docker() {
    log "Checking Docker availability..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        log "Please install Docker and try again"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker is not running"
        log "Please start Docker and try again"
        exit 1
    fi
    
    log_success "Docker is available"
}

# Check if Docker Compose is available
check_docker_compose() {
    log "Checking Docker Compose availability..."
    
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    elif docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        log_error "Docker Compose is not available"
        log "Please install Docker Compose and try again"
        exit 1
    fi
    
    log_success "Docker Compose is available: $COMPOSE_CMD"
}

# Check if port is available
check_port() {
    log "Checking if port $DB_PORT is available..."
    
    if ss -tuln | grep ":$DB_PORT " > /dev/null; then
        log_error "Port $DB_PORT is already in use"
        log "Please stop the service using port $DB_PORT or choose another port"
        exit 1
    fi
    
    log_success "Port $DB_PORT is available"
}

# Start PostgreSQL container
start_container() {
    log "Starting PostgreSQL container..."
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        log "Creating .env file from template..."
        cp env.example .env
    fi
    
    # Start the container
    $COMPOSE_CMD up -d postgres
    
    log_success "Container started"
}

# Wait for PostgreSQL to be ready
wait_for_postgres() {
    log "Waiting for PostgreSQL to be ready..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker exec $CONTAINER_NAME pg_isready -U $DB_USER -d $DB_NAME > /dev/null 2>&1; then
            log_success "PostgreSQL is ready"
            return 0
        fi
        
        log "Attempt $attempt/$max_attempts - waiting for PostgreSQL..."
        sleep 2
        ((attempt++))
    done
    
    log_error "PostgreSQL failed to start within expected time"
    return 1
}

# Initialize database schema
init_database() {
    log "Initializing database schema..."
    
    # Get script directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    
    # Execute schema files
    log "Creating tables and schema..."
    docker exec -i $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME < "$PROJECT_DIR/database/schema/01_create_tables.sql"
    
    log "Inserting reference data..."
    docker exec -i $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME < "$PROJECT_DIR/database/schema/02_insert_reference_data.sql"
    
    log "Creating views and functions..."
    docker exec -i $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME < "$PROJECT_DIR/database/schema/03_views_and_functions.sql"
    
    log_success "Database schema initialized"
}

# Load sample data
load_sample_data() {
    log "Loading sample data..."
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    
    docker exec -i $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME < "$PROJECT_DIR/database/examples/sample_data.sql"
    
    log_success "Sample data loaded"
}

# Show connection information
show_connection_info() {
    log_success "Docker PostgreSQL setup completed!"
    echo
    echo "Container Information:"
    echo "  Container Name: $CONTAINER_NAME"
    echo "  Image: postgres:latest"
    echo "  Status: $(docker inspect -f '{{.State.Status}}' $CONTAINER_NAME)"
    echo
    echo "Database Connection:"
    echo "  Host: localhost"
    echo "  Port: $DB_PORT"
    echo "  Database: $DB_NAME"
    echo "  Username: $DB_USER"
    echo "  Password: $DB_PASSWORD"
    echo
    echo "Connection string:"
    echo "  psql -h localhost -p $DB_PORT -U $DB_USER -d $DB_NAME"
    echo
    echo "Container management:"
    echo "  Start:   $COMPOSE_CMD up -d postgres"
    echo "  Stop:    $COMPOSE_CMD stop postgres"
    echo "  Logs:    $COMPOSE_CMD logs -f postgres"
    echo "  Shell:   docker exec -it $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME"
    echo
}

# Stop container
stop_container() {
    log "Stopping PostgreSQL container..."
    $COMPOSE_CMD stop postgres
    log_success "Container stopped"
}

# Remove container and volumes
remove_container() {
    log "Removing PostgreSQL container and volumes..."
    
    read -p "This will remove all data! Are you sure? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        $COMPOSE_CMD down -v
        log_success "Container and volumes removed"
    else
        log "Operation cancelled"
    fi
}

# Show container status
show_status() {
    log "Container status:"
    $COMPOSE_CMD ps postgres
    echo
    
    if docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}" | grep -q $CONTAINER_NAME; then
        log "Container is running"
        
        # Test database connection
        if docker exec $CONTAINER_NAME pg_isready -U $DB_USER -d $DB_NAME > /dev/null 2>&1; then
            log_success "Database is accessible"
            
            # Show basic stats
            echo
            echo "Database Statistics:"
            docker exec $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -c "
                SELECT 
                    'Strains' as table_name, 
                    COUNT(*) as record_count 
                FROM lysobacter.strains WHERE is_active = TRUE
                UNION ALL
                SELECT 
                    'Test Categories' as table_name, 
                    COUNT(*) as record_count 
                FROM lysobacter.test_categories
                UNION ALL
                SELECT 
                    'Tests' as table_name, 
                    COUNT(*) as record_count 
                FROM lysobacter.tests WHERE is_active = TRUE;
            " 2>/dev/null || log "Database not yet initialized"
        else
            log_warning "Container is running but database is not accessible"
        fi
    else
        log_warning "Container is not running"
    fi
}

# Show logs
show_logs() {
    log "Showing PostgreSQL logs..."
    $COMPOSE_CMD logs -f postgres
}

# Main function
main() {
    case "${1:-start}" in
        start)
            log "Starting Lysobacter PostgreSQL Docker setup..."
            check_docker
            check_docker_compose
            check_port
            start_container
            wait_for_postgres
            init_database
            show_connection_info
            ;;
        
        start-with-sample)
            log "Starting Lysobacter PostgreSQL Docker setup with sample data..."
            check_docker
            check_docker_compose
            check_port
            start_container
            wait_for_postgres
            init_database
            load_sample_data
            show_connection_info
            ;;
            
        stop)
            check_docker
            check_docker_compose
            stop_container
            ;;
            
        restart)
            check_docker
            check_docker_compose
            stop_container
            sleep 2
            start_container
            wait_for_postgres
            ;;
            
        remove)
            check_docker
            check_docker_compose
            remove_container
            ;;
            
        status)
            check_docker
            check_docker_compose
            show_status
            ;;
            
        logs)
            check_docker
            check_docker_compose
            show_logs
            ;;
            
        init)
            check_docker
            wait_for_postgres
            init_database
            ;;
            
        sample)
            check_docker
            wait_for_postgres
            load_sample_data
            ;;
            
        info)
            show_connection_info
            ;;
            
        help|--help|-h)
            echo "Lysobacter PostgreSQL Docker Management"
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  start              Start PostgreSQL container and initialize database"
            echo "  start-with-sample  Start container and load sample data"
            echo "  stop               Stop PostgreSQL container"
            echo "  restart            Restart PostgreSQL container"
            echo "  remove             Remove container and all data"
            echo "  status             Show container and database status"
            echo "  logs               Show container logs"
            echo "  init               Initialize database schema (container must be running)"
            echo "  sample             Load sample data (container must be running)"
            echo "  info               Show connection information"
            echo "  help               Show this help message"
            echo ""
            exit 0
            ;;
            
        *)
            log_error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 