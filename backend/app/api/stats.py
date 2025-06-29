"""
API endpoints for providing database statistics.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func, distinct
import logging

from app.database.connection import get_database_session
from app.database.models import Strain, TestResultNumeric, TestResultBoolean, TestResultText, TestCategory, Source

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/stats/", summary="Get Dashboard Statistics")
async def get_dashboard_stats(session: AsyncSession = Depends(get_database_session)):
    """
    Retrieve aggregated statistics for the main dashboard.
    """
    try:
        # 1. Total Species (unique scientific names)
        species_query = await session.execute(
            text("SELECT COUNT(DISTINCT scientific_name) FROM lysobacter.strains")
        )
        total_species = species_query.scalar_one_or_none() or 0

        # 2. Total Strains
        strains_query = await session.execute(
            text("SELECT COUNT(*) FROM lysobacter.strains")
        )
        total_strains = strains_query.scalar_one_or_none() or 0

        # 3. Total Test Results
        numeric_results = await session.execute(text("SELECT COUNT(*) FROM lysobacter.test_results_numeric"))
        boolean_results = await session.execute(text("SELECT COUNT(*) FROM lysobacter.test_results_boolean"))
        text_results = await session.execute(text("SELECT COUNT(*) FROM lysobacter.test_results_text"))
        total_test_results = (numeric_results.scalar_one() or 0) + \
                             (boolean_results.scalar_one() or 0) + \
                             (text_results.scalar_one() or 0)

        # 4. Total Test Categories
        categories_query = await session.execute(
            text("SELECT COUNT(*) FROM lysobacter.test_categories")
        )
        total_categories = categories_query.scalar_one_or_none() or 0
        
        # 5. Total Sources
        sources_query = await session.execute(
            text("SELECT COUNT(*) FROM lysobacter.sources")
        )
        total_sources = sources_query.scalar_one_or_none() or 0

        return {
            "total_species": total_species,
            "total_strains": total_strains,
            "total_test_results": total_test_results,
            "total_categories": total_categories,
            "total_sources": total_sources,
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard statistics: {e}", exc_info=True)
        return {"error": "Could not retrieve statistics"} 