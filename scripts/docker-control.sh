#!/bin/bash

# Lysobacter Docker Control Script
# Universal script for managing the entire Docker-based system

set -e

# Configuration
PROJECT_NAME="lysobacter"
COMPOSE_FILE="docker-compose.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Emoji
ROCKET='🚀'
STOP_SIGN='🛑'
GEAR='⚙️'
CHECK='✅'
CROSS='❌'
INFO='ℹ️'
WARN='⚠️'

# Logging functions
log() {
    echo -e "${BLUE}${INFO} [$(date '+%H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}${CHECK} $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}${WARN} $1${NC}"
}

log_error() {
    echo -e "${RED}${CROSS} $1${NC}"
}

log_info() {
    echo -e "${CYAN}${INFO} $1${NC}"
}

# Check if Docker and Docker Compose are available
check_requirements() {
    log "Checking system requirements..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker and try again."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not available. Please install Docker Compose and try again."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Determine compose command
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    
    log_success "System requirements met"
}

# Create environment file if it doesn't exist
setup_env() {
    if [ ! -f .env ]; then
        log "Creating .env file from template..."
        cp env.example .env 2>/dev/null || cat > .env << 'EOF'
# Lysobacter Database Environment Configuration
POSTGRES_DB=lysobacter_db
POSTGRES_USER=lysobacter_user
POSTGRES_PASSWORD=lysobacter_password
DB_PORT=5434
PGADMIN_EMAIL=admin@lysobacter.local
PGADMIN_PASSWORD=admin123
PGADMIN_PORT=8080
COMPOSE_PROJECT_NAME=lysobacter
EOF
        log_success ".env file created"
    fi
}

# Start the system
start_system() {
    log "${ROCKET} Starting Lysobacter system..."
    
    check_requirements
    setup_env
    
    # Create necessary directories
    mkdir -p backups docker/pgadmin
    
    # Create pgAdmin configuration if it doesn't exist
    if [ ! -f docker/pgadmin/servers.json ]; then
        cat > docker/pgadmin/servers.json << 'EOF'
{
  "Servers": {
    "1": {
      "Name": "Lysobacter Database",
      "Group": "Servers",
      "Host": "postgres",
      "Port": 5432,
      "MaintenanceDB": "lysobacter_db",
      "Username": "lysobacter_user",
      "SSLMode": "prefer"
    }
  }
}
EOF
    fi
    
    # Start database
    log "Starting PostgreSQL database..."
    $COMPOSE_CMD up -d postgres
    
    # Wait for database to be ready
    log "Waiting for database to be ready..."
    local attempts=0
    local max_attempts=30
    
    while [ $attempts -lt $max_attempts ]; do
        if $COMPOSE_CMD exec -T postgres pg_isready -U lysobacter_user -d lysobacter_db > /dev/null 2>&1; then
            log_success "Database is ready"
            break
        fi
        
        attempts=$((attempts + 1))
        log "Waiting... (attempt $attempts/$max_attempts)"
        sleep 2
    done
    
    if [ $attempts -eq $max_attempts ]; then
        log_error "Database failed to start within expected time"
        return 1
    fi
    
    # Initialize database schema
    log "Initializing database schema..."
    $COMPOSE_CMD run --rm db-init
    
    log_success "${ROCKET} Lysobacter system started successfully!"
    show_connection_info
}

# Start with admin interface
start_with_admin() {
    log "${ROCKET} Starting Lysobacter system with pgAdmin..."
    
    start_system
    
    log "Starting pgAdmin interface..."
    $COMPOSE_CMD --profile admin up -d pgadmin
    
    log_success "pgAdmin started on http://localhost:8080"
    log_info "Login: admin@lysobacter.local / admin123"
}

# Stop the system
stop_system() {
    log "${STOP_SIGN} Stopping Lysobacter system..."
    
    check_requirements
    
    $COMPOSE_CMD --profile admin --profile init down
    
    log_success "${STOP_SIGN} Lysobacter system stopped"
}

# Restart the system
restart_system() {
    log "${GEAR} Restarting Lysobacter system..."
    
    stop_system
    sleep 2
    start_system
}

# Show system status
show_status() {
    log "System Status:"
    echo
    
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    
    # Show running containers
    $COMPOSE_CMD ps
    echo
    
    # Check database connectivity
    if $COMPOSE_CMD exec -T postgres pg_isready -U lysobacter_user -d lysobacter_db > /dev/null 2>&1; then
        log_success "Database is accessible"
        
        # Show database statistics
        echo
        echo "Database Statistics:"
        $COMPOSE_CMD exec -T postgres psql -U lysobacter_user -d lysobacter_db -c "
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
        " 2>/dev/null || log_warning "Database not yet fully initialized"
    else
        log_warning "Database is not accessible"
    fi
}

# Show connection information
show_connection_info() {
    echo
    log_success "${CHECK} Connection Information:"
    echo
    echo "Database Connection:"
    echo "  Host: localhost"
    echo "  Port: 5434"
    echo "  Database: lysobacter_db"
    echo "  Username: lysobacter_user"
    echo "  Password: lysobacter_password"
    echo
    echo "Connection String:"
    echo "  postgresql://lysobacter_user:lysobacter_password@localhost:5434/lysobacter_db"
    echo
    echo "Docker Commands:"
    echo "  Connect to DB: $COMPOSE_CMD exec postgres psql -U lysobacter_user -d lysobacter_db"
    echo "  View logs:     $COMPOSE_CMD logs -f postgres"
    echo "  Stop system:   $0 stop"
    echo
}

# Show logs
show_logs() {
    check_requirements
    
    case "${2:-postgres}" in
        postgres|db|database)
            log "Showing PostgreSQL logs..."
            $COMPOSE_CMD logs -f postgres
            ;;
        pgadmin|admin)
            log "Showing pgAdmin logs..."
            $COMPOSE_CMD logs -f pgadmin
            ;;
        all)
            log "Showing all logs..."
            $COMPOSE_CMD logs -f
            ;;
        *)
            log_error "Unknown service: ${2}. Use: postgres, pgadmin, or all"
            exit 1
            ;;
    esac
}

# Connect to database shell
connect_db() {
    check_requirements
    
    log "Connecting to database shell..."
    $COMPOSE_CMD exec postgres psql -U lysobacter_user -d lysobacter_db
}

# Create backup
create_backup() {
    check_requirements
    
    local backup_name="lysobacter_backup_$(date +%Y%m%d_%H%M%S).sql.gz"
    
    log "Creating backup: $backup_name"
    
    mkdir -p backups
    
    $COMPOSE_CMD exec -T postgres pg_dump -U lysobacter_user lysobacter_db | gzip > "backups/$backup_name"
    
    log_success "Backup created: backups/$backup_name"
}

# Restore from backup
restore_backup() {
    if [ -z "$2" ]; then
        log_error "Please specify backup file: $0 restore <backup_file>"
        exit 1
    fi
    
    local backup_file="$2"
    
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    check_requirements
    
    log_warning "This will replace all data in the database!"
    read -p "Are you sure? [y/N] " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "Restoring from backup: $backup_file"
        
        gunzip -c "$backup_file" | $COMPOSE_CMD exec -T postgres psql -U lysobacter_user -d lysobacter_db
        
        log_success "Backup restored successfully"
    else
        log "Restore cancelled"
    fi
}

# Clean system (remove containers and volumes)
clean_system() {
    log_warning "This will remove all containers, volumes, and data!"
    read -p "Are you sure? [y/N] " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        check_requirements
        
        log "Removing system..."
        $COMPOSE_CMD --profile admin --profile init down -v --remove-orphans
        
        # Remove dangling images
        docker image prune -f > /dev/null 2>&1 || true
        
        log_success "System cleaned"
    else
        log "Clean cancelled"
    fi
}

# Install Python dependencies
install_deps() {
    log "Installing Python dependencies..."
    
    if [ -f requirements.txt ]; then
        pip install -r requirements.txt
        log_success "Python dependencies installed"
    else
        log_warning "requirements.txt not found"
    fi
}

# Show help
show_help() {
    echo "${BLUE}Lysobacter Docker Control Script${NC}"
    echo "================================"
    echo
    echo "Usage: $0 [command] [options]"
    echo
    echo "${YELLOW}Main Commands:${NC}"
    echo "  start              Start the system (database only)"
    echo "  start-admin        Start system with pgAdmin interface"
    echo "  stop               Stop the entire system"
    echo "  restart            Restart the system"
    echo "  status             Show system status and statistics"
    echo
    echo "${YELLOW}Database Commands:${NC}"
    echo "  connect            Connect to database shell"
    echo "  backup             Create database backup"
    echo "  restore <file>     Restore from backup file"
    echo
    echo "${YELLOW}System Commands:${NC}"
    echo "  logs [service]     Show logs (postgres|pgadmin|all)"
    echo "  clean              Remove all containers and data"
    echo "  install-deps       Install Python dependencies"
    echo "  info               Show connection information"
    echo
    echo "${YELLOW}Examples:${NC}"
    echo "  $0 start           # Start database system"
    echo "  $0 start-admin     # Start with web admin interface"
    echo "  $0 logs postgres   # Show database logs"
    echo "  $0 backup          # Create backup"
    echo "  $0 restore backups/backup.sql.gz"
    echo
    echo "${YELLOW}Access URLs:${NC}"
    echo "  Database: localhost:5434"
    echo "  pgAdmin:  http://localhost:8080 (when started with start-admin)"
    echo
}

# Main function
main() {
    case "${1:-help}" in
        start)
            start_system
            ;;
        start-admin)
            start_with_admin
            ;;
        stop)
            stop_system
            ;;
        restart)
            restart_system
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "$@"
            ;;
        connect|shell)
            connect_db
            ;;
        backup)
            create_backup
            ;;
        restore)
            restore_backup "$@"
            ;;
        clean)
            clean_system
            ;;
        install-deps)
            install_deps
            ;;
        info)
            show_connection_info
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 