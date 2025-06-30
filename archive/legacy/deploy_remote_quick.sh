#!/bin/bash

# 🚀 Quick Deploy Script for CORS Fix
# ===================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RESET='\033[0m'

# Configuration
REMOTE_HOST="ssh 4feb"
REMOTE_DIR="/tmp/lysodata-miner"

echo -e "${BLUE}🚀 Quick Deploy: CORS Fix${RESET}"
echo -e "${BLUE}========================${RESET}"

# Function to run commands on remote server
run_remote() {
    $REMOTE_HOST "$1"
}

echo -e "${YELLOW}📁 Step 1: Copying updated files...${RESET}"

# Copy only changed files
scp frontend/src/services/api.ts $REMOTE_HOST:$REMOTE_DIR/frontend/src/services/
scp backend/app/core/config.py $REMOTE_HOST:$REMOTE_DIR/backend/app/core/
scp backend/app/main.py $REMOTE_HOST:$REMOTE_DIR/backend/app/

echo -e "${YELLOW}🔄 Step 2: Rebuilding and restarting services...${RESET}"

# Stop services
run_remote "cd $REMOTE_DIR && docker-compose down"

# Rebuild only backend and frontend
run_remote "cd $REMOTE_DIR && docker-compose build backend frontend"

# Start services
run_remote "cd $REMOTE_DIR && docker-compose up -d"

echo -e "${YELLOW}⏳ Step 3: Waiting for services...${RESET}"
sleep 15

echo -e "${YELLOW}🔍 Step 4: Testing services...${RESET}"

# Test backend
if run_remote "curl -sf http://localhost:8000/api/health/ >/dev/null"; then
    echo -e "${GREEN}✅ Backend is healthy${RESET}"
else
    echo -e "${RED}❌ Backend health check failed${RESET}"
    exit 1
fi

# Test frontend
if run_remote "curl -sf http://localhost:3000 >/dev/null"; then
    echo -e "${GREEN}✅ Frontend is accessible${RESET}"
else
    echo -e "${RED}❌ Frontend check failed${RESET}"
    exit 1
fi

echo -e "${GREEN}🎉 CORS Fix Deployed Successfully!${RESET}"
echo -e "${GREEN}===================================${RESET}"
echo -e "${YELLOW}🌐 Frontend: http://89.169.171.236:3000${RESET}"
echo -e "${YELLOW}🔌 Backend: http://89.169.171.236:8000${RESET}"
echo ""
echo -e "${BLUE}💡 Changes made:${RESET}"
echo -e "  • Frontend API URLs now use relative paths in production"
echo -e "  • Backend CORS allows requests from 89.169.171.236"
echo -e "  • Automatic development/production detection" 