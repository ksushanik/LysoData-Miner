"""
LysoData-Miner Backend
======================
Modern FastAPI service for Lysobacter strain database management and identification.

Features:
- Strain browsing and search
- Test-based strain identification
- Modern async architecture
- PostgreSQL integration
- Scientific data validation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from app.core.config import settings
from app.database.connection import engine, get_database_status
from app.api import strains, tests, identification, health, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🧬 Starting LysoData-Miner Backend...")
    
    # Test database connection
    try:
        status = await get_database_status()
        if status["connected"]:
            print(f"✅ Connected to PostgreSQL: {status['database']}")
            print(f"📊 Found {status.get('tables', 0)} tables in lysobacter schema")
        else:
            print("❌ Database connection failed")
    except Exception as e:
        print(f"⚠️ Database connection warning: {e}")
    
    print("🚀 LysoData-Miner Backend ready!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down LysoData-Miner Backend...")


# Create FastAPI application
app = FastAPI(
    title="LysoData-Miner API",
    description="""
    **Modern web service for Lysobacter strain database management**
    
    This API provides comprehensive tools for:
    - 🔍 **Strain identification** based on laboratory test results
    - 📊 **Data management** for bacterial strain collections  
    - 🧪 **Test result analysis** across multiple categories
    - 📈 **Scientific reporting** and data export
    
    Built with FastAPI + PostgreSQL for high performance and scientific accuracy.
    """,
    version="1.0.0",
    contact={
        "name": "LysoData-Miner Development Team",
        "email": "support@lysodata-miner.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list + ["http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router, prefix="/api", tags=["System Health"])
app.include_router(strains.router, prefix="/api", tags=["Strains"])
app.include_router(tests.router, prefix="/api", tags=["Tests"])
app.include_router(identification.router, prefix="/api", tags=["Identification"])
app.include_router(stats.router, prefix="/api/stats", tags=["Statistics"])


@app.get("/", summary="Root endpoint", tags=["Root"])
async def root():
    """Root endpoint with service information"""
    return {
        "service": "LysoData-Miner Backend",
        "version": "1.0.0",
        "description": "Modern FastAPI service for Lysobacter strain database",
        "features": [
            "Strain browsing and search",
            "Test-based identification", 
            "Data management",
            "Scientific reporting"
        ],
        "docs": "/api/docs",
        "redoc": "/api/redoc",
        "openapi": "/api/openapi.json"
    }


@app.get("/api", summary="API Information", tags=["Root"])
async def api_info():
    """API information and available endpoints"""
    return {
        "api": "LysoData-Miner",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health/ - System health and database status",
            "strains": "/api/strains/ - Strain management and browsing",
            "tests": "/api/tests/ - Test categories and definitions", 
            "identification": "/api/identification/ - Strain identification by tests",
            "stats": "/api/stats/ - Statistics and analysis"
        },
        "database": "PostgreSQL with lysobacter schema",
        "documentation": {
            "swagger": "/api/docs",
            "redoc": "/api/redoc"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 