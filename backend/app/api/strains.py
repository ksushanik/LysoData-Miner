"""
Strains API endpoints
====================
CRUD operations and search functionality for bacterial strains.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, func, or_, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
import json
import logging
import traceback

from app.database.connection import get_database_session
from app.models.strain import Strain, StrainCollection
from app.models.reference import DataSource, CollectionNumber
from app.models.test import Test, TestValue
from app.models.result import TestResultBoolean, TestResultNumeric, TestResultText
from app.core.config import settings

router = APIRouter()


@router.get("/strains/", summary="List Strains")
@router.get("/strains", include_in_schema=False)
async def list_strains(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=settings.MAX_RESULTS_PER_PAGE, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search in strain identifier, scientific name, or description"),
    source_id: Optional[int] = Query(None, description="Filter by data source ID"),
    active_only: Optional[bool] = Query(True, description="Return only active strains"),
    scientific_name: Optional[str] = Query(None, description="Filter by scientific name"),
    db: AsyncSession = Depends(get_database_session)
):
    """Get list of bacterial strains with optional filtering and search"""
    try:
        # Build base query with relationships
        query = select(Strain).options(
            selectinload(Strain.data_source),
            selectinload(Strain.collections).selectinload(StrainCollection.collection_number)
        )
        
        # Apply filters
        filters = []
        
        if active_only:
            filters.append(Strain.is_active == True)
        
        if source_id:
            filters.append(Strain.source_id == source_id)
        
        if scientific_name:
            filters.append(Strain.scientific_name == scientific_name)
        
        # Apply search
        if search:
            search_term = f"%{search}%"
            search_filter = or_(
                Strain.strain_identifier.ilike(search_term),
                Strain.scientific_name.ilike(search_term),
                Strain.common_name.ilike(search_term),
                Strain.description.ilike(search_term)
            )
            filters.append(search_filter)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Get total count for pagination
        count_query = select(func.count(Strain.strain_id))
        if filters:
            count_query = count_query.where(and_(*filters))
        
        total_result = await db.execute(count_query)
        total_count = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(Strain.strain_identifier).offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        strains = result.scalars().all()
        
        # Format response
        strain_list = []
        for strain in strains:
            strain_data = {
                "strain_id": strain.strain_id,
                "strain_identifier": strain.strain_identifier,
                "scientific_name": strain.scientific_name,
                "common_name": strain.common_name,
                "description": strain.description,
                "isolation_source": strain.isolation_source,
                "isolation_location": strain.isolation_location,
                "isolation_date": strain.isolation_date.isoformat() if strain.isolation_date else None,
                "gc_content_range": strain.gc_content_range,
                "is_active": strain.is_active,
                "data_source": {
                    "source_id": strain.data_source.source_id,
                    "source_name": strain.data_source.source_name,
                    "source_type": strain.data_source.source_type
                } if strain.data_source else None,
                "collection_numbers": [
                    {
                        "collection_code": sc.collection_number.collection_code,
                        "collection_number": sc.collection_number.collection_number,
                        "full_identifier": sc.collection_number.full_identifier,
                        "is_primary": sc.is_primary
                    }
                    for sc in strain.collections
                ] if strain.collections else []
            }
            strain_list.append(strain_data)
        
        return {
            "strains": strain_list,
            "pagination": {
                "total": total_count,
                "skip": skip,
                "limit": limit,
                "has_next": skip + limit < total_count,
                "has_previous": skip > 0
            }
        }
        
    except Exception as e:
        logging.error(f"Error retrieving strains: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving strains: {str(e)}"
        )


@router.get("/strains/{strain_id}", summary="Get Strain Details")
async def get_strain(
    strain_id: int,
    db: AsyncSession = Depends(get_database_session)
):
    """Get detailed information about a specific strain"""
    try:
        # Build query with relationships to eagerly load all necessary data
        query = select(Strain).options(
            selectinload(Strain.data_source),
            selectinload(Strain.collections).selectinload(StrainCollection.collection_number),
            selectinload(Strain.boolean_results).options(
                selectinload(TestResultBoolean.test).selectinload(Test.category),
                selectinload(TestResultBoolean.test_value).selectinload(TestValue.test)
            ),
            selectinload(Strain.numeric_results).options(
                selectinload(TestResultNumeric.test).selectinload(Test.category)
            ),
            selectinload(Strain.text_results).options(
                selectinload(TestResultText.test).selectinload(Test.category)
            )
        )
        
        query = query.where(Strain.strain_id == strain_id)
        
        result = await db.execute(query)
        strain = result.scalar_one_or_none()
        
        if not strain:
            raise HTTPException(
                status_code=404,
                detail=f"Strain with ID {strain_id} not found"
            )
        
        # Format basic strain data
        strain_data = {
            "strain_id": strain.strain_id,
            "strain_identifier": strain.strain_identifier,
            "scientific_name": strain.scientific_name,
            "common_name": strain.common_name,
            "description": strain.description,
            "isolation_source": strain.isolation_source,
            "isolation_location": strain.isolation_location,
            "isolation_date": strain.isolation_date.isoformat() if strain.isolation_date else None,
            "gc_content_range": strain.gc_content_range,
            "notes": strain.notes,
            "is_active": strain.is_active,
            "created_at": strain.created_at.isoformat() if strain.created_at else None,
            "updated_at": strain.updated_at.isoformat() if strain.updated_at else None,
            "data_source": {
                "source_name": strain.data_source.source_name,
            } if strain.data_source else None,
            "collection_numbers": [
                {
                    "collection_name": sc.collection_number.collection_name if sc.collection_number else "N/A",
                    "collection_number": sc.collection_number.collection_number if sc.collection_number else "N/A",
                }
                for sc in strain.collections
            ] if strain.collections else []
        }
        
        # Collect and format test results
        test_results = []
        if strain.boolean_results:
            for res in strain.boolean_results:
                if res.test is None or not res.test.is_active:
                    continue
                test_results.append({
                    "test_name": res.test.test_name,
                    "result": res.test_value.value_name if res.test_value else "N/A",
                    "category": res.test.category.description if res.test.category else "Uncategorized"
                })
        if strain.numeric_results:
            for res in strain.numeric_results:
                if res.test is None or not res.test.is_active:
                    continue
                # Формируем уникальное имя с учётом value_type (min/max/optimal/single)
                value_type_label = ''
                if res.value_type and res.value_type.lower() != 'single':
                    # Переводим на человекочитаемый вид
                    mapping = {
                        'minimum': 'мин',
                        'maximum': 'макс',
                        'optimal': 'опт'
                    }
                    value_type_label = f" ({mapping.get(res.value_type.lower(), res.value_type)})"
                test_results.append({
                    "test_name": f"{res.test.test_name}{value_type_label}",
                    "result": f"{res.numeric_value} {res.measurement_unit or ''}".strip(),
                    "category": res.test.category.description if res.test.category else "Uncategorized"
                })
        if strain.text_results:
            for res in strain.text_results:
                if res.test is None or not res.test.is_active:
                    continue
                test_results.append({
                    "test_name": res.test.test_name,
                    "result": res.text_value,
                    "category": res.test.category.description if res.test.category else "Uncategorized"
                })
            
        return {
            "strain": strain_data,
            "test_results": sorted(test_results, key=lambda x: (x['category'], x['test_name']))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error retrieving strain details for ID {strain_id}: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving strain details: {str(e)}"
        )


@router.get("/strains/search", summary="Advanced Strain Search")
async def search_strains(
    query: str = Query(..., description="Search query"),
    categories: Optional[str] = Query(None, description="Comma-separated category names to search in"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: AsyncSession = Depends(get_database_session)
):
    """
    Advanced full-text search across strains and their test results.
    
    Searches in:
    - Strain identifiers and names
    - Test results and categories
    - Collection numbers
    - Source information
    """
    try:
        # This would use the existing search function from the database
        # For now, implement basic search
        search_term = f"%{query}%"
        
        strain_query = select(Strain).options(
            selectinload(Strain.data_source),
            selectinload(Strain.collections).selectinload(StrainCollection.collection_number)
        ).where(
            or_(
                Strain.strain_identifier.ilike(search_term),
                Strain.scientific_name.ilike(search_term),
                Strain.description.ilike(search_term)
            )
        ).limit(limit)
        
        result = await db.execute(strain_query)
        strains = result.scalars().all()
        
        # Format results
        results = []
        for strain in strains:
            results.append({
                "strain_id": strain.strain_id,
                "strain_identifier": strain.strain_identifier,
                "scientific_name": strain.scientific_name,
                "description": strain.description,
                "match_score": 1.0,  # Placeholder for actual scoring
                "data_source": strain.data_source.source_name if strain.data_source else None
            })
        
        return {
            "query": query,
            "results": results,
            "total_found": len(results),
            "search_categories": categories.split(",") if categories else ["all"]
        }
        
    except Exception as e:
        logging.error(f"Error during advanced search: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="An error occurred during search.")


@router.get("/species", summary="List unique scientific names")
async def list_species(
    active_only: Optional[bool] = Query(True, description="Return only active strains"),
    db: AsyncSession = Depends(get_database_session)
):
    """Return list of distinct scientific names with strain counts."""
    try:
        filters = []
        if active_only:
            filters.append(Strain.is_active == True)

        stmt = select(
            Strain.scientific_name,
            func.count(Strain.strain_id).label("strain_count")
        )
        if filters:
            stmt = stmt.where(and_(*filters))
        stmt = stmt.group_by(Strain.scientific_name).order_by(Strain.scientific_name)

        result = await db.execute(stmt)
        species_rows = result.all()

        species_list = [
            {"scientific_name": row.scientific_name, "strain_count": row.strain_count}
            for row in species_rows
        ]
        return {"species": species_list, "total": len(species_list)}
    except Exception as e:
        logging.error(f"Error fetching species list: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to retrieve species list") 