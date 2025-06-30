"""
Strains API endpoints
====================
CRUD operations and search functionality for bacterial strains.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, func, or_, and_, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any, Literal, Union, Annotated
import json
import logging
import traceback
from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal

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
    include_duplicates: bool = Query(False, description="Include strains marked as duplicates"),
    db: AsyncSession = Depends(get_database_session)
):
    """Get list of bacterial strains with optional filtering and search"""
    try:
        # Subquery to find master strains (those that have duplicates pointing to them)
        master_strain_subquery = select(Strain.master_strain_id).where(Strain.master_strain_id.isnot(None)).distinct().alias("master_ids")

        # Build base query with relationships
        query = select(
            Strain,
            (Strain.strain_id.in_(select(master_strain_subquery.c.master_strain_id))).label("is_master")
        ).options(
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
        
        if not include_duplicates:
            filters.append(Strain.is_duplicate == False)
        
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
        
        # --- REVISED COUNT LOGIC ---
        # Build count query from the main query to ensure filters are consistent
        count_query = select(func.count()).select_from(query.order_by(None).alias("main_query"))
        total_result = await db.execute(count_query)
        total_count = total_result.scalar_one()

        # Apply pagination and ordering to the main query
        query = query.order_by(Strain.strain_identifier).offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        strains_with_master_flag = result.all()
        
        # --- REVISED RESPONSE FORMATTING ---
        strain_list = [
            {
                "strain_id": strain.strain_id,
                "strain_identifier": strain.strain_identifier,
                "scientific_name": strain.scientific_name,
                "is_duplicate": strain.is_duplicate,
                "is_master": is_master and not strain.is_duplicate,
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
                    "source_type": strain.data_source.source_type,
                } if strain.data_source else None,
                "collection_numbers": [
                    {
                        "collection_code": sc.collection_number.collection_code,
                        "collection_number": sc.collection_number.collection_number,
                        "full_identifier": sc.collection_number.full_identifier,
                        "is_primary": sc.is_primary,
                    }
                    for sc in strain.collections
                ] if strain.collections else [],
            }
            for strain, is_master in strains_with_master_flag
        ]
        
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
        
        # Always exclude null scientific names
        filters.append(Strain.scientific_name.is_not(None))

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


class StrainIdsRequest(BaseModel):
    strain_ids: List[int] = Field(..., description="List of strain IDs to fetch (max 20)")

@router.post("/strains/batch", summary="Fetch multiple strains by IDs")
async def get_strains_batch(
    payload: StrainIdsRequest,
    db: AsyncSession = Depends(get_database_session)
):
    """Return detailed data for multiple strains (max 20)."""
    ids = payload.strain_ids[:20]
    if not ids:
        raise HTTPException(status_code=400, detail="strain_ids list is empty")

    try:
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
        ).where(Strain.strain_id.in_(ids))

        result = await db.execute(query)
        strains = result.scalars().all()

        formatted = []
        for s in strains:
            formatted.append({
                "strain_id": s.strain_id,
                "strain_identifier": s.strain_identifier,
                "scientific_name": s.scientific_name,
                "common_name": s.common_name,
                "is_active": s.is_active,
                "description": s.description,
                "test_results": [
                    {
                        "test_name": r.test.test_name if r.test else None,
                        "result": r.test_value.value_name if r.test_value else None,
                        "category": r.test.category.description if r.test and r.test.category else None
                    } for r in s.boolean_results or []
                ] + [
                    {
                        "test_name": r.test.test_name if r.test else None,
                        "result": str(r.numeric_value),
                        "category": r.test.category.description if r.test and r.test.category else None
                    } for r in s.numeric_results or []
                ] + [
                    {
                        "test_name": r.test.test_name if r.test else None,
                        "result": r.text_value,
                        "category": r.test.category.description if r.test and r.test.category else None
                    } for r in s.text_results or []
                ]
            })
        return {"strains": formatted}
    except Exception as e:
        logging.error(f"Error fetching batch strains: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to retrieve strains batch")


# ----------------------------
# Pydantic Schemas for CRUD
# ----------------------------


class StrainBase(BaseModel):
    strain_identifier: Optional[str] = Field(None, max_length=100, description="Unique strain code, e.g. ATCC 29482")
    scientific_name: Optional[str] = None
    common_name: Optional[str] = None
    description: Optional[str] = None
    isolation_source: Optional[str] = None
    isolation_location: Optional[str] = None
    isolation_date: Optional[date] = None
    source_id: Optional[int] = None
    gc_content_min: Optional[Decimal] = None
    gc_content_max: Optional[Decimal] = None
    gc_content_optimal: Optional[Decimal] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = True


class StrainCreate(StrainBase):
    strain_identifier: str = Field(..., max_length=100)
    test_results: Optional[List["TestResultIn"]] = None


class StrainUpdate(StrainBase):
    test_results: Optional[List["TestResultIn"]] = None


# === Test result input schemas ===

class BooleanResultIn(BaseModel):
    type: Literal['boolean'] = 'boolean'
    test_id: int = Field(..., gt=0)
    result_code: str = Field(..., max_length=10)


class NumericResultIn(BaseModel):
    type: Literal['numeric'] = 'numeric'
    test_id: int = Field(..., gt=0)
    value_type: Literal['minimum', 'maximum', 'optimal', 'single']
    numeric_value: Decimal
    measurement_unit: Optional[str] = None


class TextResultIn(BaseModel):
    type: Literal['text'] = 'text'
    test_id: int = Field(..., gt=0)
    text_value: str


TestResultIn = Annotated[Union[BooleanResultIn, NumericResultIn, TextResultIn], Field(discriminator='type')]

# rebuild models to resolve forward refs (Pydantic v2)
StrainCreate.model_rebuild()
StrainUpdate.model_rebuild()


# ------------------------------------------------
# CREATE STRAIN
# ------------------------------------------------


@router.post("/strains/", status_code=201, summary="Create new strain")
async def create_strain(payload: StrainCreate, db: AsyncSession = Depends(get_database_session)):
    """
    Creates a new strain along with its associated test results.
    """
    try:
        # Check uniqueness
        dup_check = await db.execute(select(Strain).where(Strain.strain_identifier == payload.strain_identifier))
        if dup_check.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Strain with this identifier already exists")

        new_strain = Strain(
            strain_identifier=payload.strain_identifier,
            scientific_name=payload.scientific_name,
            common_name=payload.common_name,
            description=payload.description,
            isolation_source=payload.isolation_source,
            isolation_location=payload.isolation_location,
            isolation_date=payload.isolation_date,
            source_id=payload.source_id,
            gc_content_min=payload.gc_content_min,
            gc_content_max=payload.gc_content_max,
            gc_content_optimal=payload.gc_content_optimal,
            notes=payload.notes,
            is_active=payload.is_active if payload.is_active is not None else True,
        )

        db.add(new_strain)
        await db.flush()  # get id

        await _persist_test_results(db, new_strain.strain_id, payload.test_results)

        await db.commit()
        return {"strain_id": new_strain.strain_id}

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error creating strain: {e}\n{traceback.format_exc()}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create strain")


# ------------------------------------------------
# UPDATE STRAIN
# ------------------------------------------------


@router.patch("/strains/{strain_id}/update/", summary="Update strain")
async def update_strain(strain_id: int, payload: StrainUpdate, db: AsyncSession = Depends(get_database_session)):
    """
    Updates an existing strain's information and its test results.
    This method uses PATCH and allows for partial updates.
    """
    try:
        result = await db.execute(select(Strain).where(Strain.strain_id == strain_id))
        strain = result.scalar_one_or_none()
        if not strain:
            raise HTTPException(status_code=404, detail="Strain not found")

        # Check uniqueness on strain_identifier if changed
        if payload.strain_identifier and payload.strain_identifier != strain.strain_identifier:
            dup_check = await db.execute(select(Strain).where(Strain.strain_identifier == payload.strain_identifier))
            if dup_check.scalar_one_or_none():
                raise HTTPException(status_code=409, detail="Another strain with this identifier already exists")

        update_data = payload.dict(exclude_unset=True, exclude={'test_results'})
        for field, value in update_data.items():
            setattr(strain, field, value)

        # Handle test results update
        if payload.test_results is not None:
            # First, clear existing results for this strain
            await db.execute(delete(TestResultBoolean).where(TestResultBoolean.strain_id == strain_id))
            await db.execute(delete(TestResultNumeric).where(TestResultNumeric.strain_id == strain_id))
            await db.execute(delete(TestResultText).where(TestResultText.strain_id == strain_id))
            # Then, persist new results
            if payload.test_results:
                 await _persist_test_results(db, strain_id, payload.test_results)

        await db.commit()
        
        return {"message": f"Strain {strain_id} updated successfully"}

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logging.error(f"Error updating strain {strain_id}: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )


# ------------------------------------------------
# DELETE (SOFT) STRAIN
# ------------------------------------------------


@router.delete("/strains/{strain_id}", summary="Deactivate/Delete strain")
async def delete_strain(strain_id: int, soft: bool = Query(True, description="Soft delete (set is_active=False)"), db: AsyncSession = Depends(get_database_session)):
    """Deactivate (soft delete) or permanently delete a strain"""
    try:
        result = await db.execute(select(Strain).where(Strain.strain_id == strain_id))
        strain = result.scalar_one_or_none()
        if not strain:
            raise HTTPException(status_code=404, detail="Strain not found")

        if soft:
            strain.is_active = False
            await db.commit()
            return {"detail": "Strain deactivated"}
        else:
            await db.delete(strain)
            await db.commit()
            return {"detail": "Strain permanently deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting strain {strain_id}: {e}\n{traceback.format_exc()}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete strain")


# ------------------------------------------------
# Helper to persist test results
# ------------------------------------------------


async def _persist_test_results(db: AsyncSession, strain_id: int, results: List[TestResultIn]):
    if not results:
        return
    for res in results:
        # validate test exists and active
        test_obj = await db.scalar(select(Test).where(Test.test_id == res.test_id, Test.is_active == True))
        if not test_obj:
            raise HTTPException(status_code=400, detail=f"Test ID {res.test_id} not found or inactive")

        if res.type == 'boolean':
            # find value id
            val_obj = await db.scalar(select(TestValue).where(TestValue.test_id == res.test_id, TestValue.value_code == res.result_code))
            if not val_obj:
                raise HTTPException(status_code=400, detail=f"Invalid result code '{res.result_code}' for test {res.test_id}")
            db.add(TestResultBoolean(strain_id=strain_id, test_id=res.test_id, value_id=val_obj.value_id))

        elif res.type == 'numeric':
            db.add(TestResultNumeric(
                strain_id=strain_id,
                test_id=res.test_id,
                value_type=res.value_type,
                numeric_value=res.numeric_value,
                measurement_unit=res.measurement_unit
            ))

        elif res.type == 'text':
            db.add(TestResultText(strain_id=strain_id, test_id=res.test_id, text_value=res.text_value)) 