#!/bin/bash

# 🧬 LysoData-Miner Remote Deployment Script
# ==========================================

set -e

# Colors for output
BLUE='\033[34m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
RESET='\033[0m'

# Configuration
REMOTE_HOST="4feb"
REMOTE_DIR="/home/user/lysodata-miner"
LOCAL_PROJECT_DIR="$(pwd)"

echo -e "${BLUE}🚀 LysoData-Miner Remote Deployment${RESET}"
echo -e "${BLUE}===================================${RESET}"
echo ""

# Function to run command on remote server
run_remote() {
    echo -e "${YELLOW}[REMOTE]${RESET} $1"
    ssh $REMOTE_HOST "$1"
}

# Function to check if command exists on remote
command_exists() {
    run_remote "command -v $1 >/dev/null 2>&1"
}

echo -e "${GREEN}📋 Step 1: Checking remote server prerequisites${RESET}"

# Check Docker
if command_exists docker; then
    echo -e "${GREEN}✅ Docker is installed${RESET}"
else
    echo -e "${RED}❌ Docker is not installed on remote server${RESET}"
    echo "Please install Docker first: https://docs.docker.com/install/"
    exit 1
fi

# Check Docker Compose
if command_exists docker-compose; then
    echo -e "${GREEN}✅ Docker Compose is installed${RESET}"
else
    echo -e "${RED}❌ Docker Compose is not installed on remote server${RESET}"
    echo "Please install Docker Compose first"
    exit 1
fi

# Check ports availability
echo -e "${GREEN}📋 Step 2: Checking port availability${RESET}"

PORTS=(3000 8000 5434 8082)
for port in "${PORTS[@]}"; do
    if run_remote "(echo >/dev/tcp/localhost/$port) &>/dev/null"; then
        echo -e "${RED}❌ Port $port is already in use${RESET}"
        echo "Please check running services and free the port"
        exit 1
    else
        echo -e "${GREEN}✅ Port $port is available${RESET}"
    fi
done

echo -e "${GREEN}📋 Step 3: Preparing remote directory${RESET}"

# Create remote directory
run_remote "mkdir -p $REMOTE_DIR"
run_remote "cd $REMOTE_DIR && pwd"

echo -e "${GREEN}📋 Step 4: Copying project files${RESET}"

# Copy project files
echo -e "${YELLOW}📁 Copying Docker configuration...${RESET}"
scp docker-compose.production.yml $REMOTE_HOST:$REMOTE_DIR/docker-compose.yml
scp env.remote.example $REMOTE_HOST:$REMOTE_DIR/.env
scp Makefile.production $REMOTE_HOST:$REMOTE_DIR/Makefile

echo -e "${YELLOW}📁 Copying backend...${RESET}"
scp -r backend/ $REMOTE_HOST:$REMOTE_DIR/

echo -e "${YELLOW}📁 Copying frontend...${RESET}"
scp -r frontend/ $REMOTE_HOST:$REMOTE_DIR/

echo -e "${YELLOW}📁 Copying database schema...${RESET}"
scp -r database/ $REMOTE_HOST:$REMOTE_DIR/

echo -e "${YELLOW}📁 Copying scripts...${RESET}"
scp -r scripts/ $REMOTE_HOST:$REMOTE_DIR/

echo -e "${YELLOW}📁 Creating backup directory...${RESET}"
run_remote "mkdir -p $REMOTE_DIR/backups"

echo -e "${GREEN}📋 Step 5: Building and starting services${RESET}"

# Build and start services
run_remote "cd $REMOTE_DIR && docker-compose down --remove-orphans 2>/dev/null || true"
run_remote "cd $REMOTE_DIR && docker-compose build --no-cache"
run_remote "cd $REMOTE_DIR && docker-compose up -d"

echo -e "${GREEN}📋 Step 6: Waiting for services to start${RESET}"

# Wait for services
sleep 10

echo -e "${GREEN}📋 Step 7: Checking service health${RESET}"

# Check backend health
echo -e "${YELLOW}🔍 Checking backend health...${RESET}"
if run_remote "curl -sf http://localhost:8000/api/health/ >/dev/null"; then
    echo -e "${GREEN}✅ Backend is healthy${RESET}"
else
    echo -e "${RED}❌ Backend health check failed${RESET}"
    echo "Checking logs..."
    run_remote "cd $REMOTE_DIR && docker-compose logs backend"
    exit 1
fi

# Check frontend
echo -e "${YELLOW}🔍 Checking frontend...${RESET}"
if run_remote "curl -sf http://localhost:3000 >/dev/null"; then
    echo -e "${GREEN}✅ Frontend is accessible${RESET}"
else
    echo -e "${RED}❌ Frontend check failed${RESET}"
    echo "Checking logs..."
    run_remote "cd $REMOTE_DIR && docker-compose logs frontend"
    exit 1
fi

# Check database
echo -e "${YELLOW}🔍 Checking database...${RESET}"
if run_remote "cd $REMOTE_DIR && docker-compose exec -T database pg_isready -U lysobacter_user -d lysobacter_db >/dev/null"; then
    echo -e "${GREEN}✅ Database is ready${RESET}"
else
    echo -e "${RED}❌ Database check failed${RESET}"
    run_remote "cd $REMOTE_DIR && docker-compose logs database"
    exit 1
fi

echo -e "${GREEN}📋 Step 8: Displaying service information${RESET}"

# Get database statistics
echo -e "${YELLOW}📊 Database statistics:${RESET}"
run_remote "cd $REMOTE_DIR && docker-compose exec -T database psql -U lysobacter_user -d lysobacter_db -c \"
SELECT 
  'Strains: ' || COUNT(*) as stats FROM lysobacter.strains
UNION ALL
SELECT 
  'Tests: ' || COUNT(*) FROM lysobacter.tests
UNION ALL
SELECT 
  'Results: ' || COUNT(*) FROM lysobacter.test_results_boolean;
\" -t"

echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${RESET}"
echo -e "${GREEN}=================================${RESET}"
echo ""
echo -e "${YELLOW}📊 Service URLs:${RESET}"
echo -e "   🌐 Frontend: ${GREEN}http://$(run_remote 'curl -s ifconfig.me 2>/dev/null || echo "SERVER_IP"'):3000${RESET}"
echo -e "   🔌 Backend API: ${GREEN}http://$(run_remote 'curl -s ifconfig.me 2>/dev/null || echo "SERVER_IP"'):8000${RESET}"
echo -e "   📚 API Docs: ${GREEN}http://$(run_remote 'curl -s ifconfig.me 2>/dev/null || echo "SERVER_IP"'):8000/docs${RESET}"
echo ""
echo -e "${YELLOW}💻 Management commands:${RESET}"
echo -e "   ssh $REMOTE_HOST 'cd $REMOTE_DIR && docker-compose ps'          # Status"
echo -e "   ssh $REMOTE_HOST 'cd $REMOTE_DIR && docker-compose logs -f'     # Logs"
echo -e "   ssh $REMOTE_HOST 'cd $REMOTE_DIR && docker-compose down'        # Stop"
echo -e "   ssh $REMOTE_HOST 'cd $REMOTE_DIR && docker-compose restart'     # Restart"
echo ""
echo -e "${GREEN}✅ LysoData-Miner is now running on the remote server!${RESET}" 