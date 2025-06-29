"""
API endpoints for providing database statistics.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import logging

from app.database.connection import get_database_session
from app.models import Strain, Test, TestCategory, TestResultNumeric, TestResultBoolean, TestResultText, DataSource, StrainCollection

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", summary="Get dashboard statistics")
async def get_dashboard_stats(session: AsyncSession = Depends(get_database_session)):
    """
    Returns main statistics for the dashboard.
    """
    total_strains_query = select(func.count(Strain.strain_id))
    total_categories_query = select(func.count(TestCategory.category_id))
    
    total_results_numeric_query = select(func.count(TestResultNumeric.result_id))
    total_results_boolean_query = select(func.count(TestResultBoolean.result_id))
    total_results_text_query = select(func.count(TestResultText.result_id))

    total_species_query = select(func.count(func.distinct(Strain.scientific_name)))
    total_sources_query = select(func.count(DataSource.source_id))
    total_collection_numbers_query = select(func.count(StrainCollection.strain_id))

    try:
        total_strains = (await session.execute(total_strains_query)).scalar_one()
        total_categories = (await session.execute(total_categories_query)).scalar_one()
        
        numeric_results = (await session.execute(total_results_numeric_query)).scalar_one()
        boolean_results = (await session.execute(total_results_boolean_query)).scalar_one()
        text_results = (await session.execute(total_results_text_query)).scalar_one()
        total_test_results = numeric_results + boolean_results + text_results
        
        total_species = (await session.execute(total_species_query)).scalar_one()
        total_sources = (await session.execute(total_sources_query)).scalar_one()
        total_collection_numbers = (await session.execute(total_collection_numbers_query)).scalar_one()

        return {
            "total_strains": total_strains,
            "total_test_results": total_test_results,
            "total_species": total_species,
            "total_sources": total_sources,
            "total_collection_numbers": total_collection_numbers,
            "total_categories": total_categories,
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching stats.") 