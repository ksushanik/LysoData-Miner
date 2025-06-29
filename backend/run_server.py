#!/usr/bin/env python3
"""
LysoData-Miner Server Launcher
==============================
Development server for the LysoData-Miner FastAPI backend.
"""

import uvicorn
import os
from app.core.config import settings

def main():
    """Launch the FastAPI server with optimal settings"""
    
    print("🧬 Starting LysoData-Miner Backend Server")
    print(f"📊 Database: {settings.database_url}")
    print(f"🌐 API URL: http://{settings.HOST}:{settings.PORT}{settings.API_PREFIX}")
    print(f"📚 Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print("="*60)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        use_colors=True,
        loop="asyncio"
    )

if __name__ == "__main__":
    main() 