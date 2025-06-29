#!/bin/bash

# 🔄 LysoData-Miner Auto-Deploy Watcher
# =====================================
# Monitors git repository for changes and automatically deploys to 4feb server

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
WATCH_INTERVAL=30  # seconds
DEPLOY_SCRIPT="./scripts/deployment/deploy_to_4feb.sh"
LAST_COMMIT_FILE=".last_auto_deploy_commit"
LOG_FILE="auto_deploy.log"
PID_FILE="auto_deploy.pid"

# Options
AUTO_COMMIT=false
WATCH_BRANCH="main"
DEPLOY_ON_PUSH=true
NOTIFICATION_WEBHOOK=""

# Function to show usage
show_usage() {
    echo -e "${BLUE}🔄 LysoData-Miner Auto-Deploy Watcher${RESET}"
    echo -e "${BLUE}=====================================${RESET}"
    echo ""
    echo "Usage: $0 [OPTIONS] [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start             Start the auto-deploy watcher"
    echo "  stop              Stop the auto-deploy watcher"
    echo "  status            Show watcher status"
    echo "  logs              Show auto-deploy logs"
    echo ""
    echo "Options:"
    echo "  --interval SEC    Check interval in seconds (default: 30)"
    echo "  --branch BRANCH   Branch to watch (default: main)"
    echo "  --auto-commit     Auto-commit changes before deploy"
    echo "  --webhook URL     Webhook URL for notifications"
    echo "  --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Start watching for changes"
    echo "  $0 start --interval 60      # Check every minute"
    echo "  $0 start --auto-commit      # Auto-commit changes"
    echo "  $0 stop                     # Stop the watcher"
}

# Function to log messages
log_message() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Function to send notification
send_notification() {
    local status=$1
    local message=$2
    
    log_message "INFO" "Notification: $status - $message"
    
    if [ -n "$NOTIFICATION_WEBHOOK" ]; then
        curl -s -X POST "$NOTIFICATION_WEBHOOK" \
             -H "Content-Type: application/json" \
             -d "{\"text\":\"🚀 LysoData-Miner Auto-Deploy $status: $message\"}" \
             >/dev/null 2>&1 || true
    fi
    
    # Desktop notification (if available)
    if command -v notify-send >/dev/null 2>&1; then
        notify-send "LysoData-Miner Deploy" "$status: $message" || true
    fi
}

# Function to check if watcher is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" >/dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to start the watcher
start_watcher() {
    if is_running; then
        echo -e "${YELLOW}⚠️ Auto-deploy watcher is already running${RESET}"
        return 1
    fi
    
    echo -e "${BLUE}🔄 Starting auto-deploy watcher...${RESET}"
    echo -e "${CYAN}Configuration:${RESET}"
    echo -e "  Watch interval: ${WATCH_INTERVAL}s"
    echo -e "  Branch: $WATCH_BRANCH"
    echo -e "  Auto-commit: $AUTO_COMMIT"
    echo -e "  Deploy script: $DEPLOY_SCRIPT"
    echo -e "  Log file: $LOG_FILE"
    echo ""
    
    # Start watcher in background
    nohup bash -c "
        while true; do
            if [ -f '$PID_FILE' ]; then
                watch_for_changes
                sleep $WATCH_INTERVAL
            else
                break
            fi
        done
    " >/dev/null 2>&1 &
    
    echo $! > "$PID_FILE"
    log_message "INFO" "Auto-deploy watcher started (PID: $!)"
    send_notification "STARTED" "Auto-deploy watcher is now monitoring for changes"
    
    echo -e "${GREEN}✅ Auto-deploy watcher started${RESET}"
    echo -e "${YELLOW}💡 Use '$0 logs' to monitor activity${RESET}"
    echo -e "${YELLOW}💡 Use '$0 stop' to stop the watcher${RESET}"
}

# Function to stop the watcher
stop_watcher() {
    if ! is_running; then
        echo -e "${YELLOW}⚠️ Auto-deploy watcher is not running${RESET}"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    echo -e "${BLUE}🛑 Stopping auto-deploy watcher (PID: $pid)...${RESET}"
    
    kill "$pid" 2>/dev/null || true
    rm -f "$PID_FILE"
    
    log_message "INFO" "Auto-deploy watcher stopped"
    send_notification "STOPPED" "Auto-deploy watcher has been stopped"
    
    echo -e "${GREEN}✅ Auto-deploy watcher stopped${RESET}"
}

# Function to show status
show_status() {
    echo -e "${BLUE}📊 Auto-Deploy Watcher Status${RESET}"
    echo -e "${BLUE}=============================${RESET}"
    echo ""
    
    if is_running; then
        local pid=$(cat "$PID_FILE")
        echo -e "${GREEN}Status: Running (PID: $pid)${RESET}"
        
        # Show last activity
        if [ -f "$LOG_FILE" ]; then
            echo -e "${CYAN}Last activity:${RESET}"
            tail -5 "$LOG_FILE" | sed 's/^/  /'
        fi
    else
        echo -e "${RED}Status: Not running${RESET}"
    fi
    
    echo ""
    echo -e "${CYAN}Configuration:${RESET}"
    echo -e "  Watch interval: ${WATCH_INTERVAL}s"
    echo -e "  Branch: $WATCH_BRANCH"
    echo -e "  Deploy script: $DEPLOY_SCRIPT"
    echo -e "  Log file: $LOG_FILE"
    
    if [ -f "$LAST_COMMIT_FILE" ]; then
        local last_commit=$(cat "$LAST_COMMIT_FILE")
        echo -e "  Last deployed commit: ${last_commit:0:8}"
    fi
}

# Function to show logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        echo -e "${BLUE}📋 Auto-Deploy Logs${RESET}"
        echo -e "${BLUE}===================${RESET}"
        tail -f "$LOG_FILE"
    else
        echo -e "${YELLOW}⚠️ No log file found${RESET}"
    fi
}

# Function to check for changes and deploy
watch_for_changes() {
    # Fetch latest changes
    git fetch origin >/dev/null 2>&1 || {
        log_message "ERROR" "Failed to fetch from origin"
        return 1
    }
    
    local current_commit=$(git rev-parse HEAD)
    local remote_commit=$(git rev-parse "origin/$WATCH_BRANCH")
    
    # Check if we have the last deployed commit
    local last_deployed=""
    if [ -f "$LAST_COMMIT_FILE" ]; then
        last_deployed=$(cat "$LAST_COMMIT_FILE")
    fi
    
    # Check for new commits
    if [ "$current_commit" != "$remote_commit" ]; then
        log_message "INFO" "New commits detected on origin/$WATCH_BRANCH"
        
        # Pull changes
        git pull origin "$WATCH_BRANCH" >/dev/null 2>&1 || {
            log_message "ERROR" "Failed to pull changes"
            send_notification "ERROR" "Failed to pull changes from git"
            return 1
        }
        
        current_commit=$(git rev-parse HEAD)
        log_message "INFO" "Pulled changes, current commit: ${current_commit:0:8}"
    fi
    
    # Check if we need to deploy
    if [ "$current_commit" != "$last_deployed" ]; then
        log_message "INFO" "Changes detected, starting deployment..."
        send_notification "DEPLOYING" "Starting deployment for commit ${current_commit:0:8}"
        
        # Auto-commit if requested
        if [ "$AUTO_COMMIT" = true ]; then
            if ! git diff-index --quiet HEAD --; then
                log_message "INFO" "Auto-committing local changes"
                git add -A
                git commit -m "Auto-commit before deploy $(date '+%Y-%m-%d %H:%M:%S')"
                git push origin "$WATCH_BRANCH"
                current_commit=$(git rev-parse HEAD)
            fi
        fi
        
        # Run deployment
        if "$DEPLOY_SCRIPT" --skip-tests; then
            echo "$current_commit" > "$LAST_COMMIT_FILE"
            log_message "SUCCESS" "Deployment completed successfully for commit ${current_commit:0:8}"
            send_notification "SUCCESS" "Deployment completed for commit ${current_commit:0:8}"
        else
            log_message "ERROR" "Deployment failed for commit ${current_commit:0:8}"
            send_notification "FAILED" "Deployment failed for commit ${current_commit:0:8}"
        fi
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --interval)
            WATCH_INTERVAL="$2"
            shift 2
            ;;
        --branch)
            WATCH_BRANCH="$2"
            shift 2
            ;;
        --auto-commit)
            AUTO_COMMIT=true
            shift
            ;;
        --webhook)
            NOTIFICATION_WEBHOOK="$2"
            shift 2
            ;;
        --help)
            show_usage
            exit 0
            ;;
        start)
            COMMAND="start"
            shift
            ;;
        stop)
            COMMAND="stop"
            shift
            ;;
        status)
            COMMAND="status"
            shift
            ;;
        logs)
            COMMAND="logs"
            shift
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${RESET}"
            show_usage
            exit 1
            ;;
    esac
done

# Execute command
case "${COMMAND:-}" in
    start)
        start_watcher
        ;;
    stop)
        stop_watcher
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    *)
        show_usage
        exit 1
        ;;
esac 