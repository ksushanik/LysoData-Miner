#!/usr/bin/env python3

"""
🚀 LysoData-Miner Webhook Deploy Server
=======================================
Simple HTTP server for triggering deployments via webhook calls.
"""

import os
import sys
import json
import hmac
import hashlib
import subprocess
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging

# Configuration
WEBHOOK_PORT = int(os.environ.get('WEBHOOK_PORT', 9000))
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'lysodata-webhook-secret')
DEPLOY_SCRIPT = os.environ.get('DEPLOY_SCRIPT', './scripts/deploy_to_4feb.sh')
LOG_FILE = os.environ.get('WEBHOOK_LOG_FILE', 'webhook_deploy.log')
ALLOWED_IPS = os.environ.get('ALLOWED_IPS', '').split(',') if os.environ.get('ALLOWED_IPS') else []

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class WebhookHandler(BaseHTTPRequestHandler):
    """HTTP request handler for webhook deployments"""
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")
    
    def verify_signature(self, payload, signature):
        """Verify webhook signature"""
        if not WEBHOOK_SECRET:
            return True  # No secret configured, allow all
        
        expected_signature = hmac.new(
            WEBHOOK_SECRET.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(f"sha256={expected_signature}", signature)
    
    def check_ip_allowed(self):
        """Check if client IP is allowed"""
        if not ALLOWED_IPS or ALLOWED_IPS == ['']:
            return True  # No IP restrictions
        
        client_ip = self.client_address[0]
        return client_ip in ALLOWED_IPS
    
    def send_json_response(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = json.dumps(data, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        
        if parsed_url.path == '/':
            self.send_json_response(200, {
                'service': 'LysoData-Miner Webhook Deploy Server',
                'status': 'running',
                'endpoints': {
                    '/deploy': 'POST - Trigger deployment',
                    '/status': 'GET - Check deployment status',
                    '/health': 'GET - Health check'
                },
                'timestamp': datetime.now().isoformat()
            })
        
        elif parsed_url.path == '/health':
            self.send_json_response(200, {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat()
            })
        
        elif parsed_url.path == '/status':
            # Check if deployment is running
            try:
                result = subprocess.run(['pgrep', '-f', DEPLOY_SCRIPT], 
                                     capture_output=True, text=True)
                is_deploying = bool(result.stdout.strip())
                
                self.send_json_response(200, {
                    'deploying': is_deploying,
                    'deploy_script': DEPLOY_SCRIPT,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                self.send_json_response(500, {
                    'error': f'Failed to check status: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                })
        
        else:
            self.send_json_response(404, {
                'error': 'Endpoint not found',
                'path': parsed_url.path
            })
    
    def do_POST(self):
        """Handle POST requests"""
        if not self.check_ip_allowed():
            logger.warning(f"Blocked request from unauthorized IP: {self.client_address[0]}")
            self.send_json_response(403, {
                'error': 'IP address not allowed'
            })
            return
        
        parsed_url = urlparse(self.path)
        
        if parsed_url.path == '/deploy':
            self.handle_deploy_request()
        else:
            self.send_json_response(404, {
                'error': 'Endpoint not found',
                'path': parsed_url.path
            })
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Hub-Signature-256')
        self.end_headers()
    
    def handle_deploy_request(self):
        """Handle deployment webhook request"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            payload = self.rfile.read(content_length)
            
            # Verify signature if provided
            signature = self.headers.get('X-Hub-Signature-256', '')
            if signature and not self.verify_signature(payload, signature):
                logger.warning("Invalid webhook signature")
                self.send_json_response(401, {
                    'error': 'Invalid signature'
                })
                return
            
            # Parse payload
            try:
                data = json.loads(payload.decode('utf-8')) if payload else {}
            except json.JSONDecodeError:
                data = {}
            
            # Extract deployment options
            options = data.get('options', {})
            force_build = options.get('force_build', False)
            skip_tests = options.get('skip_tests', True)
            frontend_only = options.get('frontend_only', False)
            backend_only = options.get('backend_only', False)
            
            # Build command
            deploy_cmd = [DEPLOY_SCRIPT]
            
            if force_build:
                deploy_cmd.append('--force-build')
            if skip_tests:
                deploy_cmd.append('--skip-tests')
            if frontend_only:
                deploy_cmd.append('--frontend-only')
            if backend_only:
                deploy_cmd.append('--backend-only')
            
            logger.info(f"Triggering deployment with command: {' '.join(deploy_cmd)}")
            
            # Start deployment in background
            def run_deployment():
                try:
                    result = subprocess.run(
                        deploy_cmd,
                        capture_output=True,
                        text=True,
                        timeout=1800  # 30 minutes timeout
                    )
                    
                    if result.returncode == 0:
                        logger.info("Deployment completed successfully")
                    else:
                        logger.error(f"Deployment failed with exit code {result.returncode}")
                        logger.error(f"Error output: {result.stderr}")
                
                except subprocess.TimeoutExpired:
                    logger.error("Deployment timed out after 30 minutes")
                except Exception as e:
                    logger.error(f"Deployment error: {str(e)}")
            
            # Start deployment thread
            deploy_thread = threading.Thread(target=run_deployment)
            deploy_thread.daemon = True
            deploy_thread.start()
            
            # Send immediate response
            self.send_json_response(202, {
                'status': 'accepted',
                'message': 'Deployment started',
                'command': ' '.join(deploy_cmd),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error handling deploy request: {str(e)}")
            self.send_json_response(500, {
                'error': f'Internal server error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            })

def run_server():
    """Run the webhook server"""
    server_address = ('', WEBHOOK_PORT)
    httpd = HTTPServer(server_address, WebhookHandler)
    
    logger.info(f"🚀 Starting LysoData-Miner Webhook Deploy Server")
    logger.info(f"📡 Listening on port {WEBHOOK_PORT}")
    logger.info(f"🔐 Secret configured: {'Yes' if WEBHOOK_SECRET else 'No'}")
    logger.info(f"🛡️  IP restrictions: {'Yes' if ALLOWED_IPS else 'No'}")
    logger.info(f"📜 Deploy script: {DEPLOY_SCRIPT}")
    logger.info(f"📝 Log file: {LOG_FILE}")
    
    print(f"""
🚀 LysoData-Miner Webhook Deploy Server
======================================

Server Status: Running
Port: {WEBHOOK_PORT}
Deploy Script: {DEPLOY_SCRIPT}

Available Endpoints:
  GET  /              - Server info
  GET  /health        - Health check
  GET  /status        - Deployment status
  POST /deploy        - Trigger deployment

Example Usage:
  # Simple deployment
  curl -X POST http://localhost:{WEBHOOK_PORT}/deploy

  # Deployment with options
  curl -X POST http://localhost:{WEBHOOK_PORT}/deploy \\
       -H "Content-Type: application/json" \\
       -d '{{"options": {{"force_build": true, "skip_tests": true}}}}'

  # With signature (if secret configured)
  curl -X POST http://localhost:{WEBHOOK_PORT}/deploy \\
       -H "X-Hub-Signature-256: sha256=<signature>"

Press Ctrl+C to stop the server
""")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down webhook server...")
        httpd.shutdown()

if __name__ == '__main__':
    run_server() 