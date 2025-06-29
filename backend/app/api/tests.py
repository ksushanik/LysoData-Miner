"""
Tests API endpoints
==================
Endpoints for managing test categories, tests, and their values.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any

from app.database.connection import get_database_session
from app.models.test import TestCategory, Test, TestValue

router = APIRouter()


@router.get("/tests/categories", summary="Get Test Categories")
async def get_test_categories(
    include_tests: bool = Query(False, description="Include tests in each category"),
    db: AsyncSession = Depends(get_database_session)
):
    """Get all test categories"""
    try:
        query = select(TestCategory)
        
        if include_tests:
            query = query.options(selectinload(TestCategory.tests))
        
        query = query.order_by(TestCategory.sort_order, TestCategory.category_name)
        
        result = await db.execute(query)
        categories = result.scalars().all()
        
        category_list = []
        for category in categories:
            category_data = {
                "category_id": category.category_id,
                "category_name": category.category_name,
                "description": category.description,
                "sort_order": category.sort_order
            }
            
            if include_tests:
                category_data["tests"] = [
                    {
                        "test_id": test.test_id,
                        "test_name": test.test_name,
                        "test_type": test.test_type,
                        "measurement_unit": test.measurement_unit,
                        "is_active": test.is_active
                    }
                    for test in category.tests if test.is_active
                ]
                category_data["test_count"] = len(category_data["tests"])
            
            category_list.append(category_data)
        
        return {
            "categories": category_list,
            "total_categories": len(category_list)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving test categories: {str(e)}"
        )


@router.get("/tests/", summary="Get Tests")
async def get_tests(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    test_type: Optional[str] = Query(None, description="Filter by test type"),
    db: AsyncSession = Depends(get_database_session)
):
    """Get tests with optional filtering"""
    try:
        query = select(Test).options(
            selectinload(Test.category),
            selectinload(Test.test_values)
        )
        
        # Apply filters
        filters = []
        
        if category_id:
            filters.append(Test.category_id == category_id)
        
        if test_type:
            filters.append(Test.test_type == test_type)
        
        filters.append(Test.is_active == True)
        
        if filters:
            query = query.where(*filters)
        
        query = query.order_by(Test.category_id, Test.sort_order)
        
        result = await db.execute(query)
        tests = result.scalars().all()
        
        # Format results
        test_list = []
        for test in tests:
            test_data = {
                "test_id": test.test_id,
                "category_id": test.category_id,
                "category_name": test.category.category_name,
                "test_name": test.test_name,
                "test_code": test.test_code,
                "test_type": test.test_type,
                "measurement_unit": test.measurement_unit
            }
            
            # Add possible values for boolean tests
            if test.test_type == 'boolean' and test.test_values:
                test_data["possible_values"] = [
                    {
                        "value_id": tv.value_id,
                        "value_code": tv.value_code,
                        "value_name": tv.value_name
                    }
                    for tv in sorted(test.test_values, key=lambda x: x.sort_order)
                ]
            
            test_list.append(test_data)
        
        return {"tests": test_list, "total": len(test_list)}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving tests: {str(e)}"
        )


@router.get("/tests/{test_id}/options", summary="Get Unique Options for a Test")
async def get_test_options(
    test_id: int,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Get unique result options for a specific test.
    - For 'boolean' tests, it returns predefined values.
    - For 'numeric' and 'text' tests, it returns distinct values from actual results.
    """
    try:
        # First, find the test to know its type
        test_result = await db.execute(select(Test).where(Test.test_id == test_id))
        test = test_result.scalar_one_or_none()

        if not test:
            raise HTTPException(status_code=404, detail=f"Test with ID {test_id} not found")

        options = []
        if test.test_type == 'boolean':
            # For boolean, get predefined values from test_values table
            from app.models.test import TestValue
            stmt = select(TestValue).where(TestValue.test_id == test_id).order_by(TestValue.sort_order)
            results = await db.execute(stmt)
            options = [{"value_id": v.value_id, "display_value": v.display_value} for v in results.scalars().all()]

        elif test.test_type == 'numeric':
            # For numeric, get distinct values from results
            from app.models.result import TestResultNumeric
            stmt = select(TestResultNumeric.numeric_value).where(TestResultNumeric.test_id == test_id).distinct().order_by(TestResultNumeric.numeric_value)
            results = await db.execute(stmt)
            options = [{"value_id": v, "display_value": str(v)} for v in results.scalars().all() if v is not None]

        elif test.test_type == 'text':
            # For text, get distinct values from results
            from app.models.result import TestResultText
            stmt = select(TestResultText.text_value).where(TestResultText.test_id == test_id).distinct().order_by(TestResultText.text_value)
            results = await db.execute(stmt)
            options = [{"value_id": v, "display_value": v} for v in results.scalars().all() if v]

        return {"options": options}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving options for test {test_id}: {str(e)}"
        )


@router.get("/tests/{test_id}", summary="Get Test Details")
async def get_test(
    test_id: int,
    include_values: bool = Query(True, description="Include possible values"),
    db: AsyncSession = Depends(get_database_session)
):
    """Get detailed information about a specific test"""
    try:
        query = select(Test).options(
            selectinload(Test.category)
        )
        
        if include_values:
            query = query.options(selectinload(Test.test_values))
        
        query = query.where(Test.test_id == test_id)
        
        result = await db.execute(query)
        test = result.scalar_one_or_none()
        
        if not test:
            raise HTTPException(
                status_code=404,
                detail=f"Test with ID {test_id} not found"
            )
        
        test_data = {
            "test_id": test.test_id,
            "category": {
                "category_id": test.category.category_id,
                "category_name": test.category.category_name,
                "description": test.category.description
            },
            "test_name": test.test_name,
            "test_code": test.test_code,
            "test_type": test.test_type,
            "description": test.description,
            "measurement_unit": test.measurement_unit,
            "is_active": test.is_active,
            "sort_order": test.sort_order,
            "display_name": test.display_name,
            "created_at": test.created_at.isoformat(),
            "type_properties": {
                "is_boolean": test.is_boolean,
                "is_numeric": test.is_numeric,
                "is_text": test.is_text
            }
        }
        
        # Add possible values for boolean tests
        if include_values and test.test_type == 'boolean' and test.test_values:
            test_data["possible_values"] = [
                {
                    "value_id": tv.value_id,
                    "value_code": tv.value_code,
                    "value_name": tv.value_name,
                    "description": tv.description,
                    "sort_order": tv.sort_order,
                    "display_value": tv.display_value,
                    "is_positive": tv.is_positive,
                    "is_negative": tv.is_negative,
                    "is_intermediate": tv.is_intermediate,
                    "is_no_data": tv.is_no_data
                }
                for tv in sorted(test.test_values, key=lambda x: x.sort_order)
            ]
        
        return test_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving test details: {str(e)}"
        ) 