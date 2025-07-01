# 🧬 LysoData-Miner

**Modern Web Service for Lysobacter Strain Identification and Analysis**

LysoData-Miner is a sophisticated full-stack application designed for the identification and analysis of Lysobacter bacterial strains based on comprehensive laboratory test results. Built with modern technologies, it provides researchers with an intuitive interface for strain classification and comparative analysis.

![LysoData-Miner Interface](docs/images/interface-preview.png)

## ✨ Key Features

### 🔬 **Advanced Strain Identification**
- Intelligent strain matching based on laboratory test results
- Support for multiple test types: morphological, physiological, biochemical
- Configurable tolerance levels for accurate identification
- Confidence scoring and ranking algorithms

### 📊 **Comprehensive Data Management**
- Complete PostgreSQL database with normalized schema (3NF)
- 11 specialized tables covering 6 test categories
- 38+ different laboratory tests supported
- Robust data validation and integrity checks

### 🌐 **Modern User Interface**
- Clean, scientific design with minimal visual clutter
- Responsive interface optimized for laboratory environments
- Real-time search and filtering capabilities
- Interactive data visualization

### 🚀 **High-Performance Architecture**
- FastAPI backend with async SQLAlchemy ORM
- React frontend with TypeScript and modern tooling
- Optimized database queries for fast identification
- RESTful API with comprehensive OpenAPI documentation

## 🏗️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Robust relational database
- **SQLAlchemy 2.0** - Async ORM with advanced features
- **Pydantic** - Data validation and serialization
- **Docker** - Containerized deployment

### Frontend
- **React 18** - Modern UI library
- **TypeScript** - Type-safe development
- **Vite** - Fast build tooling
- **Tailwind CSS** - Utility-first styling
- **Tanstack Query** - Powerful data fetching

### Development Tools
- **Docker Compose** - Multi-service orchestration
- **ESLint/Prettier** - Code quality and formatting
- **pytest** - Comprehensive testing framework
- **Makefile** - Simplified command management

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **Node.js 18+**
- **Docker & Docker Compose**
- **PostgreSQL** (or use Docker)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd lysobacters
make install  # Install all dependencies
```

### 2. Start Development Environment
```bash
make dev  # Starts both backend and frontend
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5434

## 📋 Available Commands

```bash
# Development
make dev-start       # Start DEV environment (backend + frontend + database)
make dev-stop        # Stop DEV environment
make dev-logs        # View development logs
make dev-rebuild     # Rebuild development containers

# Production
make prod-start      # Start PROD environment locally
make prod-stop       # Stop PROD environment
make prod-build      # Build production images

# 🚀 Deployment (to 4feb server)
make deploy          # Simple full deployment (build + migrate + update)
make deploy-quick    # Quick deployment (update containers only)
make deploy-force    # Force rebuild and deploy
make deploy-advanced # Advanced deploy with tests and checks
make deploy-dry      # Preview deployment actions (safe testing)

# Deployment Components
make deploy-build    # Build and push Docker images to Hub
make deploy-migrate  # Run database migrations on server
make deploy-update   # Update containers on server
make deploy-status   # Check deployment status
make deploy-logs     # View server logs

# Specialized Deployment
make deploy-frontend-only  # Deploy only frontend
make deploy-backend-only   # Deploy only backend

# Database Management
make db-backup       # Create database backup
make db-restore      # Restore database (BACKUP=file.sql.gz)

# Utilities
make help            # Show all available commands
```

## 🗄️ Database Schema

The application uses a comprehensive PostgreSQL schema optimized for microbiological data:

### Core Tables
- **strains** - Main bacterial strain records
- **test_categories** - Groupings for related tests
- **tests** - Individual laboratory test definitions
- **test_results_boolean** - Positive/negative test results
- **test_results_numeric** - Quantitative measurements
- **test_results_text** - Descriptive test data

### Reference Tables
- **data_sources** - Laboratory and publication sources
- **collection_numbers** - Strain collection identifiers
- **test_values** - Possible values for categorical tests

## 🔬 Supported Test Categories

1. **Morphological Properties**
   - Spore formation, cell motility, cell shape

2. **Physiological Parameters**
   - Temperature ranges (min/max/optimal)
   - pH tolerance and optima
   - Salt tolerance levels

3. **Biochemical Enzymes**
   - Catalase, oxidase, urease activity
   - Various metabolic enzymes

4. **Substrate Degradation**
   - Starch, gelatin, casein hydrolysis
   - Tween compound degradation

5. **Sugar Utilization**
   - Maltose, lactose, fructose metabolism
   - Complex carbohydrate utilization

6. **Additional Characteristics**
   - Cellulase activity
   - GC content analysis
   - Growth conditions

## 🔍 API Endpoints

### Health Monitoring
- `GET /api/health/` - Basic health check
- `GET /api/health/db` - Database health status
- `GET /api/health/database` - Detailed database info

### Strain Management
- `GET /api/strains/` - List strains with filtering
- `GET /api/strains/{id}` - Get detailed strain information
- `GET /api/strains/search` - Advanced strain search

### Test Management
- `GET /api/tests/categories` - Get test categories
- `GET /api/tests/` - List available tests
- `GET /api/tests/{id}` - Get test details

### Strain Identification
- `POST /api/identification/identify` - Identify strains by test results
- `GET /api/identification/stats` - Get identification statistics

## 📁 Project Structure

```
lysobacters/
├── backend/              # FastAPI backend application
│   ├── app/
│   │   ├── api/         # API route definitions
│   │   │   └── models/      # SQLAlchemy ORM models
│   │   ├── core/        # Core configuration
│   │   ├── database/    # Database connection and utilities
│   │   └── models/
│   ├── requirements.txt # Python dependencies
│   └── run_server.py    # Development server launcher
├── frontend/            # React frontend application
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Page components
│   │   ├── hooks/       # Custom React hooks
│   │   └── utils/       # Utility functions
│   ├── package.json     # Node.js dependencies
│   └── vite.config.ts   # Vite configuration
├── database/            # Database schema and initialization
│   ├── schema/          # SQL schema definitions
│   ├── examples/        # Sample data
│   └── init/            # Initialization scripts
├── docker-compose.yml   # Original database setup
├── docker-compose.dev.yml # Development environment
├── Makefile            # Development commands
└── README.md           # This file
```

## 🔧 Configuration

### Backend Configuration
Edit `backend/env.example` and copy to `.env`:
```bash
# Database settings
POSTGRES_HOST=localhost
POSTGRES_PORT=5434
POSTGRES_DB=lysobacter_db
POSTGRES_USER=lysobacter_user
POSTGRES_PASSWORD=lysobacter_password

# API settings
DEBUG=true
MAX_RESULTS_PER_PAGE=100
DEFAULT_TOLERANCE=2
```

### Frontend Configuration
The frontend uses Vite's environment variables. Create `frontend/.env.local`:
```bash
VITE_API_URL=http://localhost:8000
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### Type Checking
```bash
cd frontend
npm run type-check
```

## 📦 Deployment

### 🚀 **Automated Deployment to Production Server**

LysoData-Miner includes a comprehensive CI/CD deployment system that automates the entire process from code changes to running production services.

#### **Quick Start Deployment**
```bash
# Test deployment first (safe)
make deploy-dry      # Preview what will happen

# Full production deployment
make deploy-advanced # Complete deployment with tests and checks
```

#### **Deployment Process**
The automated deployment includes:

1. **🧪 Testing** - Runs backend (pytest) and frontend (npm test) tests
2. **🏗️ Building** - Creates optimized Docker images with timestamps
3. **📤 Registry** - Pushes images to Docker Hub (gimmyhat/lysodata-*)
4. **💾 Backup** - Creates database backup before deployment
5. **🔄 Update** - Downloads new images and recreates containers
6. **🗄️ Migrations** - Automatically runs Django database migrations
7. **📁 Static Files** - Collects Django static files
8. **🏥 Health Checks** - Verifies backend API and frontend accessibility

#### **Deployment Commands**

```bash
# Recommended workflow
make deploy-dry      # 1. Preview deployment (no changes made)
make deploy-advanced # 2. Full deployment with all checks

# Alternative deployment options
make deploy          # Simple deployment (build + migrate + update)
make deploy-quick    # Update containers only (fastest)
make deploy-force    # Force rebuild everything

# Component-specific deployment
make deploy-frontend-only  # Deploy only frontend changes
make deploy-backend-only   # Deploy only backend changes

# Deployment management
make deploy-status   # Check current deployment status
make deploy-logs     # View server logs
```

#### **Production Server Details**
- **Server**: 4feb (89.169.171.236)
- **Frontend**: http://89.169.171.236:3000
- **Backend API**: http://89.169.171.236:8000
- **API Docs**: http://89.169.171.236:8000/api/docs

#### **Safety Features**
- ✅ **Dry Run Mode** - Test deployments safely with `deploy-dry`
- ✅ **Automatic Backups** - Database backed up before each deployment
- ✅ **Health Checks** - Deployment fails if services don't start properly
- ✅ **Change Detection** - Only rebuilds components that have changed
- ✅ **Rollback Ready** - Backup files available for quick restoration

### Local Development
```bash
make dev-start       # Start development environment
# Make your changes...
make deploy-dry      # Test deployment first
make deploy-advanced # Deploy to production
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow TypeScript/Python typing conventions
- Write tests for new features
- Use semantic commit messages
- Ensure all lints pass before committing

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Resources

- [Lysobacter Research Papers](docs/references.md)
- [API Documentation](http://localhost:8000/docs) (when running)
- [Database Schema Documentation](docs/database-schema.md)
- [Development Setup Guide](docs/development.md)

## 📧 Support

For questions, issues, or contributions:
- Open an [issue](https://github.com/your-org/lysobacters/issues)
- Contact the development team
- Check the [documentation](docs/)

---

**Built with ❤️ for the scientific community**

*LysoData-Miner enables researchers to efficiently identify and analyze Lysobacter strains, accelerating microbiological research and discovery.* 