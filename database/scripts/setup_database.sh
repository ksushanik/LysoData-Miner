#!/bin/bash

# Lysobacter Database Setup Script
# This script creates and initializes the Lysobacter database

set -e  # Exit on any error

# Configuration
DB_NAME="lysobacter_db"
DB_USER="lysobacter_user"
DB_PASSWORD="lysobacter_password"
DB_HOST="localhost"
DB_PORT="5432"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
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

# Check if PostgreSQL is running
check_postgresql() {
    log "Checking PostgreSQL status..."
    if ! pg_isready -h "$DB_HOST" -p "$DB_PORT" >/dev/null 2>&1; then
        log_error "PostgreSQL is not running on $DB_HOST:$DB_PORT"
        log "Please start PostgreSQL and try again"
        exit 1
    fi
    log_success "PostgreSQL is running"
}

# Check if psql is available
check_psql() {
    log "Checking psql availability..."
    if ! command -v psql &> /dev/null; then
        log_error "psql command not found"
        log "Please install PostgreSQL client tools"
        exit 1
    fi
    log_success "psql is available"
}

# Create database user
create_user() {
    log "Creating database user: $DB_USER"
    
    # Check if user already exists
    if psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
        log_warning "User $DB_USER already exists"
    else
        psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
        log_success "User $DB_USER created"
    fi
}

# Create database
create_database() {
    log "Creating database: $DB_NAME"
    
    # Check if database already exists
    if psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        log_warning "Database $DB_NAME already exists"
        read -p "Do you want to recreate it? This will DELETE all existing data! (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log "Dropping existing database..."
            psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -c "DROP DATABASE $DB_NAME;"
            log "Creating new database..."
            psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
            log_success "Database $DB_NAME recreated"
        else
            log "Using existing database"
        fi
    else
        psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
        log_success "Database $DB_NAME created"
    fi
}

# Execute SQL file
execute_sql_file() {
    local file_path="$1"
    local description="$2"
    
    log "Executing $description: $(basename $file_path)"
    
    if [ ! -f "$file_path" ]; then
        log_error "File not found: $file_path"
        exit 1
    fi
    
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$file_path"
    
    if [ $? -eq 0 ]; then
        log_success "$description completed"
    else
        log_error "$description failed"
        exit 1
    fi
}

# Run database setup
setup_database() {
    log "Setting up database schema and data..."
    
    # Get script directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    SCHEMA_DIR="$SCRIPT_DIR/../schema"
    EXAMPLES_DIR="$SCRIPT_DIR/../examples"
    
    # Execute schema files in order
    execute_sql_file "$SCHEMA_DIR/01_create_tables.sql" "Creating tables and schema"
    execute_sql_file "$SCHEMA_DIR/02_insert_reference_data.sql" "Inserting reference data"
    execute_sql_file "$SCHEMA_DIR/03_views_and_functions.sql" "Creating views and functions"
    
    # Ask if user wants sample data
    read -p "Do you want to load sample data for testing? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        execute_sql_file "$EXAMPLES_DIR/sample_data.sql" "Loading sample data"
    fi
}

# Verify installation
verify_installation() {
    log "Verifying installation..."
    
    # Test database connection
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        log_success "Database connection successful"
    else
        log_error "Database connection failed"
        exit 1
    fi
    
    # Count tables
    table_count=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'lysobacter';")
    log "Tables created: $table_count"
    
    # Count test categories
    category_count=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT COUNT(*) FROM lysobacter.test_categories;")
    log "Test categories: $category_count"
    
    # Count tests
    test_count=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT COUNT(*) FROM lysobacter.tests;")
    log "Tests configured: $test_count"
    
    log_success "Installation verification completed"
}

# Show connection info
show_connection_info() {
    log_success "Database setup completed successfully!"
    echo
    echo "Connection information:"
    echo "  Host: $DB_HOST"
    echo "  Port: $DB_PORT"
    echo "  Database: $DB_NAME"
    echo "  Username: $DB_USER"
    echo "  Password: $DB_PASSWORD"
    echo
    echo "To connect to the database:"
    echo "  PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
    echo
    echo "To test the setup, run some sample queries:"
    echo "  SELECT * FROM lysobacter.test_categories;"
    echo "  SELECT * FROM lysobacter.v_category_statistics;"
    echo
}

# Main execution
main() {
    log "Starting Lysobacter Database Setup"
    log "================================="
    
    # Pre-flight checks
    check_postgresql
    check_psql
    
    # Database setup
    create_user
    create_database
    setup_database
    
    # Verification
    verify_installation
    show_connection_info
    
    log_success "Setup completed successfully!"
}

# Command line options
case "${1:-}" in
    --help|-h)
        echo "Lysobacter Database Setup Script"
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --verify       Only verify existing installation"
        echo "  --clean        Clean setup (recreate database)"
        echo ""
        echo "Environment variables:"
        echo "  DB_NAME        Database name (default: lysobacter_db)"
        echo "  DB_USER        Database user (default: lysobacter_user)"
        echo "  DB_PASSWORD    Database password (default: lysobacter_password)"
        echo "  DB_HOST        Database host (default: localhost)"
        echo "  DB_PORT        Database port (default: 5432)"
        exit 0
        ;;
    --verify)
        check_postgresql
        check_psql
        verify_installation
        exit 0
        ;;
    --clean)
        log "Clean setup mode - will recreate database"
        main
        ;;
    "")
        main
        ;;
    *)
        log_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac 