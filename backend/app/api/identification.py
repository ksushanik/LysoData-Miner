"""
Strain Identification API
=========================
Core functionality for identifying bacterial strains based on test results.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, func, and_, or_, case
from sqlalchemy.orm import aliased
import time
import logging
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

from app.database.connection import get_database_session
from app.models import Strain, Test, TestResultBoolean, TestResultNumeric, TestResultText, TestValue
from app.core.config import settings

# Setup logger
logger = logging.getLogger(__name__)

router = APIRouter()


# New data models for flexible test input
class NumericTestValue(BaseModel):
    exact: Optional[float] = None
    range: Optional[Dict[str, float]] = None  # {"min": 15, "max": 42}
    mode: str = Field(..., description="'exact' or 'range'")


class BooleanTestValue(BaseModel):
    value: str = Field(..., description="'+', '-', '+/-', or 'n.d.'")


class TestValueInput(BaseModel):
    test_id: int
    test_code: str
    test_type: str = Field(..., description="'boolean', 'numeric', or 'text'")
    boolean_value: Optional[BooleanTestValue] = None
    numeric_value: Optional[NumericTestValue] = None
    text_value: Optional[str] = None


class IdentificationRequest(BaseModel):
    test_values: List[TestValueInput] = Field(..., description="List of test values for identification.")
    limit: int = Field(20, ge=1, le=100)
    tolerance: float = Field(2.0, ge=0, le=10.0, description="Tolerance for numeric values")
    min_confidence: float = Field(0.1, ge=0, le=1.0)


# Legacy support for old format
class LegacyIdentificationRequest(BaseModel):
    test_results: Dict[int, str] = Field(..., description="Dictionary of test results, mapping test_id to its value.")
    limit: int = Field(20, ge=1, le=100)
    tolerance: int = Field(0, ge=0, le=10)
    min_confidence: float = Field(0.1, ge=0, le=1.0)


class MatchDetail(BaseModel):
    test_name: str
    strain_result: Optional[str]
    query_result: str
    match_status: str  # 'match', 'mismatch', 'not_found', 'partial_match'


class StrainMatch(BaseModel):
    strain: Dict[str, Any]
    score: float
    match_count: int
    mismatch_count: int
    query_test_count: int
    details: List[MatchDetail]


def build_numeric_comparison_sql(test_value: TestValueInput, tolerance: float) -> str:
    """Build SQL conditions for numeric value comparison with improved gradation"""
    if test_value.numeric_value.mode == 'exact':
        exact_val = test_value.numeric_value.exact
        # 15% tolerance for partial match
        partial_tolerance = exact_val * 0.15
        return f"""
            CASE WHEN asr.strain_result IS NULL THEN 'not_found'
                 WHEN CAST(asr.strain_result AS numeric) = {exact_val} THEN 'match'
                 WHEN ABS(CAST(asr.strain_result AS numeric) - {exact_val}) <= {partial_tolerance} THEN 'partial_match'
                 ELSE 'mismatch'
            END
        """
    elif test_value.numeric_value.mode == 'range':
        min_val = test_value.numeric_value.range['min']
        max_val = test_value.numeric_value.range['max']
        # 15% tolerance for partial match
        range_span = max_val - min_val
        partial_tolerance = range_span * 0.15
        return f"""
            CASE WHEN asr.strain_result IS NULL THEN 'not_found'
                 WHEN CAST(asr.strain_result AS numeric) BETWEEN {min_val} AND {max_val} THEN 'match'
                 WHEN CAST(asr.strain_result AS numeric) BETWEEN {min_val - partial_tolerance} AND {max_val + partial_tolerance} THEN 'partial_match'
                 ELSE 'mismatch'
            END
        """
    else:
        return "'mismatch'"


@router.post("/identification/identify", 
             summary="Identify Strains by Test Results")
async def identify_strains(
    request: Union[IdentificationRequest, LegacyIdentificationRequest],
    db: AsyncSession = Depends(get_database_session)
):
    """
    Identify bacterial strains by comparing provided test results against the database.
    Supports both new flexible format and legacy format.
    """
    start_time = time.time()
    
    logger.debug(f"Received request: {request}")
    logger.debug(f"Request type: {type(request).__name__}")
    
    # Convert legacy format to new format if needed
    if hasattr(request, 'test_results'):
        # Legacy format conversion
        test_values = []
        for test_id, value in request.test_results.items():
            # Try to determine test type from database
            test_query = select(Test).where(Test.test_id == test_id)
            test_result = await db.execute(test_query)
            test = test_result.scalar()
            
            if not test:
                continue
                
            if test.test_type == 'boolean':
                test_values.append(TestValueInput(
                    test_id=test_id,
                    test_code=test.test_code,
                    test_type='boolean',
                    boolean_value=BooleanTestValue(value=value)
                ))
            elif test.test_type == 'numeric':
                try:
                    numeric_val = float(value)
                    test_values.append(TestValueInput(
                        test_id=test_id,
                        test_code=test.test_code,
                        test_type='numeric',
                        numeric_value=NumericTestValue(exact=numeric_val, mode='exact')
                    ))
                except ValueError:
                    continue
            else:  # text
                test_values.append(TestValueInput(
                    test_id=test_id,
                    test_code=test.test_code,
                    test_type='text',
                    text_value=value
                ))
        
        # Convert other parameters
        limit = request.limit
        tolerance = float(request.tolerance)
        min_confidence = request.min_confidence
    else:
        # New format
        test_values = request.test_values
        limit = request.limit
        tolerance = request.tolerance
        min_confidence = request.min_confidence
    
    if not test_values:
        raise HTTPException(status_code=422, detail="No test values provided.")

    # Build the complex query based on test types
    test_ids = [tv.test_id for tv in test_values]
    
    # Build query data for different test types
    boolean_conditions = []
    numeric_conditions = []
    text_conditions = []
    query_data_parts = []
    
    for tv in test_values:
        if tv.test_type == 'boolean' and tv.boolean_value:
            boolean_conditions.append(f"({tv.test_id}, '{tv.boolean_value.value}')")
            query_data_parts.append(f"({tv.test_id}, '{tv.boolean_value.value}', 'boolean')")
        elif tv.test_type == 'numeric' and tv.numeric_value:
            if tv.numeric_value.mode == 'exact':
                query_data_parts.append(f"({tv.test_id}, '{tv.numeric_value.exact}', 'numeric')")
            else:
                range_str = f"{tv.numeric_value.range['min']}-{tv.numeric_value.range['max']}"
                query_data_parts.append(f"({tv.test_id}, '{range_str}', 'numeric_range')")
        elif tv.test_type == 'text' and tv.text_value:
            text_conditions.append(f"({tv.test_id}, '{tv.text_value}')")
            query_data_parts.append(f"({tv.test_id}, '{tv.text_value}', 'text')")

    if not query_data_parts:
        raise HTTPException(status_code=422, detail="No valid test values provided.")

    query_data_cte = ", ".join(query_data_parts)
    
    # Build match conditions for different test types
    match_conditions = []
    for tv in test_values:
        if tv.test_type == 'boolean':
            match_conditions.append(f"""
                WHEN qd.test_id = {tv.test_id} AND t.test_type = 'boolean' THEN
                    CASE WHEN asr.strain_result IS NULL THEN 'not_found'
                         WHEN lower(asr.strain_result) = lower('{tv.boolean_value.value}') THEN 'match'
                         ELSE 'mismatch'
                    END
            """)
        elif tv.test_type == 'numeric':
            match_conditions.append(f"""
                WHEN qd.test_id = {tv.test_id} AND t.test_type = 'numeric' THEN
                    {build_numeric_comparison_sql(tv, tolerance)}
            """)
        elif tv.test_type == 'text':
            match_conditions.append(f"""
                WHEN qd.test_id = {tv.test_id} AND t.test_type = 'text' THEN
                    CASE WHEN asr.strain_result IS NULL THEN 'not_found'
                         WHEN lower(asr.strain_result) LIKE lower('%{tv.text_value}%') THEN 'match'
                         ELSE 'mismatch'
                    END
            """)

    match_case_statement = " ".join(match_conditions)
    
    sql_query = text(f"""
        WITH query_data (test_id, query_result, query_type) AS (
            VALUES {query_data_cte}
        ),
        all_strain_results AS (
            -- Boolean results
            SELECT b.strain_id, b.test_id, t.test_name, v.value_code AS strain_result
            FROM lysobacter.test_results_boolean b
            JOIN lysobacter.test_values v ON b.value_id = v.value_id
            JOIN lysobacter.tests t ON b.test_id = t.test_id
            WHERE b.test_id = ANY(:test_ids)
            UNION ALL
            -- Numeric results (all value types)
            SELECT n.strain_id, n.test_id, t.test_name, 
                   n.numeric_value::text AS strain_result
            FROM lysobacter.test_results_numeric n
            JOIN lysobacter.tests t ON n.test_id = t.test_id
            WHERE n.test_id = ANY(:test_ids)
            UNION ALL
            -- Text results
            SELECT txt.strain_id, txt.test_id, t.test_name, txt.text_value AS strain_result
            FROM lysobacter.test_results_text txt
            JOIN lysobacter.tests t ON txt.test_id = t.test_id
            WHERE txt.test_id = ANY(:test_ids)
        ),
        comparison AS (
            SELECT
                s.strain_id,
                s.strain_identifier,
                s.scientific_name,
                s.common_name,
                s.isolation_source,
                qd.test_id,
                qd.query_result,
                qd.query_type,
                asr.strain_result,
                t.test_name,
                CASE 
                    {match_case_statement}
                    ELSE 'not_found'
                END AS match_status
            FROM query_data qd
            JOIN lysobacter.tests t ON qd.test_id = t.test_id
            CROSS JOIN lysobacter.strains s
            LEFT JOIN all_strain_results asr ON qd.test_id = asr.test_id AND s.strain_id = asr.strain_id
            WHERE s.is_active = true
        ),
        ranked_strains AS (
            SELECT
                strain_id,
                strain_identifier,
                scientific_name,
                common_name,
                isolation_source,
                COUNT(*) FILTER (WHERE match_status = 'match') AS match_count,
                COUNT(*) FILTER (WHERE match_status = 'partial_match') AS partial_match_count,
                COUNT(*) FILTER (WHERE match_status = 'mismatch') AS mismatch_count,
                COUNT(*) FILTER (WHERE match_status = 'not_found') AS not_found_count,
                json_agg(json_build_object(
                    'test_name', test_name,
                    'strain_result', strain_result,
                    'query_result', query_result,
                    'query_type', query_type,
                    'match_status', match_status
                )) AS details
            FROM comparison
            GROUP BY strain_id, strain_identifier, scientific_name, common_name, isolation_source
        )
        SELECT *,
               ROUND(
                   (match_count * 1.0 + partial_match_count * 0.85) / 
                   GREATEST(match_count + partial_match_count + mismatch_count, 1) * 100, 2
               ) AS match_percentage,
               ROUND(
                   (match_count * 2.0 + partial_match_count * 1.7 - mismatch_count * 0.5) /
                   GREATEST(match_count + partial_match_count + mismatch_count + not_found_count, 1), 3
               ) AS confidence_score
        FROM ranked_strains
        WHERE (match_count + partial_match_count) > 0
        ORDER BY confidence_score DESC, match_percentage DESC, match_count DESC
        LIMIT :limit
    """)

    try:
        result = await db.execute(sql_query, {"test_ids": tuple(test_ids), "limit": limit})
        matches = result.mappings().all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

    final_results = []
    query_test_count = len(test_values)
    
    for match in matches:
        if match['confidence_score'] < min_confidence:
            continue

        # Calculate additional metrics
        total_tests = match['match_count'] + match['partial_match_count'] + match['mismatch_count']
        conflicting_tests = match['mismatch_count']
        
        final_results.append({
            "strain_id": match['strain_id'],
            "strain_identifier": match['strain_identifier'],
            "scientific_name": match['scientific_name'],
            "common_name": match['common_name'],
            "isolation_source": match['isolation_source'],
            "match_percentage": float(match['match_percentage']),
            "matching_tests": match['match_count'],
            "partial_matching_tests": match['partial_match_count'],
            "total_tests": total_tests,
            "conflicting_tests": conflicting_tests,
            "confidence_score": float(match['confidence_score']),
            "details": match['details']
        })

    return {
        "results": final_results,
        "total_results": len(final_results),
        "query_summary": {
            "total_test_values": query_test_count,
            "boolean_tests": len([tv for tv in test_values if tv.test_type == 'boolean']),
            "numeric_tests": len([tv for tv in test_values if tv.test_type == 'numeric']),
            "text_tests": len([tv for tv in test_values if tv.test_type == 'text'])
        },
        "execution_time_ms": round((time.time() - start_time) * 1000, 2)
    }


@router.get("/identification/stats", summary="Get Identification Statistics")
async def get_identification_stats(
    db: AsyncSession = Depends(get_database_session)
):
    """Get statistics about the identification system"""
    try:
        # Count total strains
        strain_count_query = select(func.count(Strain.strain_id)).where(Strain.is_active == True)
        strain_count_result = await db.execute(strain_count_query)
        total_strains = strain_count_result.scalar()
        
        # Count test results by type
        boolean_count_query = select(func.count(TestResultBoolean.result_id))
        boolean_count_result = await db.execute(boolean_count_query)
        boolean_results = boolean_count_result.scalar()
        
        numeric_count_query = select(func.count(TestResultNumeric.result_id))
        numeric_count_result = await db.execute(numeric_count_query)
        numeric_results = numeric_count_result.scalar()
        
        text_count_query = select(func.count(TestResultText.result_id))
        text_count_result = await db.execute(text_count_query)
        text_results = text_count_result.scalar()
        
        # Count available tests
        test_count_query = select(func.count(Test.test_id)).where(Test.is_active == True)
        test_count_result = await db.execute(test_count_query)
        total_tests = test_count_result.scalar()
        
        return {
            "total_strains": total_strains,
            "total_tests": total_tests,
            "test_results": {
                "boolean": boolean_results,
                "numeric": numeric_results, 
                "text": text_results,
                "total": boolean_results + numeric_results + text_results
            },
            "system_status": "operational"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}") 