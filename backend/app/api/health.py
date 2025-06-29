"""
Health check API endpoints
=========================
System health monitoring and database status endpoints.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import time

from app.database.connection import get_database_status, health_check

router = APIRouter()


@router.get("/health/", summary="Basic Health Check")
async def basic_health():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "LysoData-Miner Backend",
        "version": "1.0.0",
        "timestamp": time.time()
    }


@router.get("/health/db", summary="Database Health Check")
async def database_health():
    """Comprehensive database health check"""
    try:
        health_data = await health_check()
        
        if health_data["status"] == "healthy":
            return health_data
        elif health_data["status"] == "degraded":
            raise HTTPException(
                status_code=503,
                detail="Database is in degraded state"
            )
        else:
            raise HTTPException(
                status_code=503,
                detail="Database is unhealthy"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/health/database", summary="Database Connection Status") 
async def database_status():
    """Get detailed database connection status"""
    try:
        status = await get_database_status()
        
        if not status["connected"]:
            raise HTTPException(
                status_code=503,
                detail="Database connection failed"
            )
        
        return {
            "status": "connected",
            "database_info": status,
            "lysobacter_schema": {
                "exists": status["tables"] > 0,
                "table_count": status["tables"],
                "tables": status.get("table_names", [])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database status check failed: {str(e)}"
        ) 