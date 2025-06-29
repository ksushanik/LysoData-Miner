"""
Database connection and session management
==========================================
Async PostgreSQL connection using SQLAlchemy 2.0 for the lysobacter database.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text, inspect
from typing import AsyncGenerator, Dict, Any
import logging
import traceback

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create async engine with connection pooling
engine = create_async_engine(
    settings.async_database_url,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for SQLAlchemy models
Base = declarative_base()


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session.
    
    Yields:
        AsyncSession: Database session for use in FastAPI dependencies
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}\n{traceback.format_exc()}")
            await session.rollback()
            raise


async def get_database_status() -> Dict[str, Any]:
    """
    Check database connection and get basic status information.
    
    Returns:
        Dict containing database status information
    """
    status = {
        "connected": False,
        "database": settings.POSTGRES_DB,
        "schema": settings.POSTGRES_SCHEMA,
        "host": settings.POSTGRES_HOST,
        "port": settings.POSTGRES_PORT,
        "tables": 0,
        "error": None
    }
    
    try:
        async with AsyncSessionLocal() as session:
            # Test basic connection
            result = await session.execute(text("SELECT version()"))
            version = result.scalar()
            status["version"] = version
            status["connected"] = True
            
            # Count tables in lysobacter schema
            table_count_query = text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = :schema
            """)
            result = await session.execute(table_count_query, {"schema": settings.POSTGRES_SCHEMA})
            status["tables"] = result.scalar() or 0
            
            # Get table names
            tables_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = :schema
                ORDER BY table_name
            """)
            result = await session.execute(tables_query, {"schema": settings.POSTGRES_SCHEMA})
            status["table_names"] = [row[0] for row in result.fetchall()]
            
            logger.info(f"Database connection successful: {status['tables']} tables found")
            
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        status["error"] = str(e)
    
    return status


async def check_schema_exists() -> bool:
    """
    Check if the lysobacter schema exists.
    
    Returns:
        bool: True if schema exists, False otherwise
    """
    try:
        async with AsyncSessionLocal() as session:
            query = text("""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.schemata 
                    WHERE schema_name = :schema
                )
            """)
            result = await session.execute(query, {"schema": settings.POSTGRES_SCHEMA})
            return result.scalar() or False
    except Exception as e:
        logger.error(f"Error checking schema existence: {e}")
        return False


async def get_table_info(table_name: str) -> Dict[str, Any]:
    """
    Get information about a specific table in the lysobacter schema.
    
    Args:
        table_name: Name of the table to inspect
        
    Returns:
        Dict containing table information
    """
    info = {
        "exists": False,
        "columns": [],
        "row_count": 0,
        "error": None
    }
    
    try:
        async with AsyncSessionLocal() as session:
            # Check if table exists
            exists_query = text("""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = :schema AND table_name = :table
                )
            """)
            result = await session.execute(exists_query, {
                "schema": settings.POSTGRES_SCHEMA,
                "table": table_name
            })
            info["exists"] = result.scalar() or False
            
            if info["exists"]:
                # Get column information
                columns_query = text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = :schema AND table_name = :table
                    ORDER BY ordinal_position
                """)
                result = await session.execute(columns_query, {
                    "schema": settings.POSTGRES_SCHEMA,
                    "table": table_name
                })
                info["columns"] = [
                    {
                        "name": row[0],
                        "type": row[1],
                        "nullable": row[2] == "YES",
                        "default": row[3]
                    }
                    for row in result.fetchall()
                ]
                
                # Get row count
                count_query = text(f"SELECT COUNT(*) FROM {settings.POSTGRES_SCHEMA}.{table_name}")
                result = await session.execute(count_query)
                info["row_count"] = result.scalar() or 0
                
    except Exception as e:
        logger.error(f"Error getting table info for {table_name}: {e}")
        info["error"] = str(e)
    
    return info


async def execute_raw_query(query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Execute a raw SQL query safely.
    
    Args:
        query: SQL query string
        params: Query parameters
        
    Returns:
        Dict containing query results
    """
    result_data = {
        "success": False,
        "rows": [],
        "row_count": 0,
        "columns": [],
        "error": None
    }
    
    try:
        async with AsyncSessionLocal() as session:
            if params is None:
                params = {}
            
            result = await session.execute(text(query), params)
            
            if result.returns_rows:
                rows = result.fetchall()
                result_data["rows"] = [dict(row._mapping) for row in rows]
                result_data["row_count"] = len(rows)
                result_data["columns"] = list(result.keys()) if rows else []
            else:
                result_data["row_count"] = result.rowcount
            
            result_data["success"] = True
            
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        result_data["error"] = str(e)
    
    return result_data


# Database health check function for monitoring
async def health_check() -> Dict[str, Any]:
    """
    Comprehensive database health check.
    
    Returns:
        Dict containing health check results
    """
    health = {
        "status": "unhealthy",
        "database": {
            "connected": False,
            "response_time_ms": None,
            "schema_exists": False,
            "essential_tables": {}
        },
        "error": None
    }
    
    essential_tables = [
        "strains",
        "test_categories", 
        "tests",
        "test_results_boolean",
        "test_results_numeric"
    ]
    
    try:
        import time
        start_time = time.time()
        
        # Test database connection and get status
        db_status = await get_database_status()
        health["database"]["connected"] = db_status["connected"]
        health["database"]["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
        
        if db_status["connected"]:
            # Check schema existence
            health["database"]["schema_exists"] = await check_schema_exists()
            
            # Check essential tables
            for table in essential_tables:
                table_info = await get_table_info(table)
                health["database"]["essential_tables"][table] = {
                    "exists": table_info["exists"],
                    "row_count": table_info["row_count"]
                }
            
            # Determine overall health
            all_tables_exist = all(
                health["database"]["essential_tables"][table]["exists"]
                for table in essential_tables
            )
            
            if health["database"]["schema_exists"] and all_tables_exist:
                health["status"] = "healthy"
            else:
                health["status"] = "degraded"
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        health["error"] = str(e)
    
    return health 