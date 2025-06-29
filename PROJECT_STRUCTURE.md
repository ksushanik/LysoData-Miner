# LysoData-Miner Project Structure

```
lysobacters/
├── README.md                    # Main project documentation
├── Makefile                     # Main project commands
├── .gitignore                   # Git ignore rules
│
├── backend/                     # FastAPI backend application
│   ├── app/                     # Application source code
│   ├── database/               # Database scripts and data
│   ├── Dockerfile              # Backend container config
│   └── requirements.txt        # Python dependencies
│
├── frontend/                    # React frontend application
│   ├── src/                    # Frontend source code
│   ├── public/                 # Static assets
│   ├── Dockerfile              # Frontend container config
│   └── package.json            # Node.js dependencies
│
├── config/                      # Configuration files
│   ├── docker/                 # Docker compose files
│   │   ├── docker-compose.yml  # Development
│   │   ├── docker-compose.production.yml
│   │   └── docker-compose.hub.yml
│   ├── environment/            # Environment templates
│   │   ├── env.example
│   │   ├── env.production.example
│   │   └── env.hub.example
│   └── makefiles/              # Specialized makefiles
│       ├── Makefile.development
│       ├── Makefile.production
│       └── Makefile.cicd
│
├── scripts/                     # Automation scripts
│   ├── deployment/             # Deployment automation
│   │   ├── deploy_to_4feb.sh   # Main deployment script
│   │   ├── watch_and_deploy.sh # Auto-deployment watcher
│   │   └── webhook_server.py   # Webhook deployment server
│   ├── database/               # Database utilities
│   │   ├── simple_import.py    # Simple data import
│   │   └── test_import.py      # Import testing
│   └── utilities/              # General utilities
│
├── docs/                        # Documentation
│   ├── guides/                 # User guides
│   ├── api/                    # API documentation
│   ├── deployment/             # Deployment guides
│   │   ├── CI_CD_GUIDE.md
│   │   ├── CI_CD_QUICK_START.md
│   │   ├── PRODUCTION_DEPLOYMENT.md
│   │   └── DOCKER_HUB_DEPLOYMENT.md
│   └── database/               # Database documentation
│       ├── DATABASE_STRUCTURE.md
│       └── TEMPLATE_SUMMARY.txt
│
├── backups/                     # Backup files
│   ├── database/               # Database backups
│   └── logs/                   # Log backups
│
├── logs/                        # Application logs
│   ├── deployment.log
│   ├── webhook.log
│   └── auto_deploy.log
│
├── data/                        # Data files
└── database/                    # Database initialization
```

## Key Changes

### ✅ Organized Structure
- All documentation in `docs/` with categorization
- Configuration files in `config/` by type
- Scripts organized by purpose in `scripts/`
- Backups and logs in dedicated directories

### ✅ Consolidated Management
- Single main `Makefile` with includes
- Specialized makefiles in `config/makefiles/`
- Clear separation of concerns

### ✅ Removed Duplication
- Eliminated duplicate deployment scripts
- Consolidated similar functionality
- Removed outdated files

## Usage

```bash
# Main commands
make help                    # Show all available commands
make dev-setup              # Setup development environment

# Development
make -f config/makefiles/Makefile.development dev-start
make -f config/makefiles/Makefile.development dev-stop

# Production deployment
make -f config/makefiles/Makefile.production deploy

# CI/CD operations
make -f config/makefiles/Makefile.cicd deploy
make -f config/makefiles/Makefile.cicd watch-start
```
