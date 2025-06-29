-- Additional views and functions for Lysobacter database

-- ========================================
-- STATISTICAL VIEWS
-- ========================================

-- Statistics by test category
CREATE VIEW lysobacter.v_category_statistics AS
SELECT 
    tc.category_name,
    tc.description,
    COUNT(t.test_id) as total_tests,
    COUNT(CASE WHEN t.is_active = TRUE THEN 1 END) as active_tests,
    COUNT(DISTINCT trb.strain_id) + COUNT(DISTINCT trn.strain_id) + COUNT(DISTINCT trt.strain_id) as strains_with_data
FROM lysobacter.test_categories tc
LEFT JOIN lysobacter.tests t ON tc.category_id = t.category_id
LEFT JOIN lysobacter.test_results_boolean trb ON t.test_id = trb.test_id
LEFT JOIN lysobacter.test_results_numeric trn ON t.test_id = trn.test_id
LEFT JOIN lysobacter.test_results_text trt ON t.test_id = trt.test_id
GROUP BY tc.category_id, tc.category_name, tc.description
ORDER BY tc.sort_order;

-- Test completion statistics
CREATE VIEW lysobacter.v_test_completion AS
SELECT 
    t.test_id,
    t.test_name,
    t.test_type,
    tc.category_name,
    COUNT(DISTINCT s.strain_id) as total_strains,
    COUNT(DISTINCT CASE 
        WHEN t.test_type = 'boolean' THEN trb.strain_id
        WHEN t.test_type = 'numeric' THEN trn.strain_id
        WHEN t.test_type = 'text' THEN trt.strain_id
    END) as tested_strains,
    ROUND(
        COUNT(DISTINCT CASE 
            WHEN t.test_type = 'boolean' THEN trb.strain_id
            WHEN t.test_type = 'numeric' THEN trn.strain_id
            WHEN t.test_type = 'text' THEN trt.strain_id
        END) * 100.0 / NULLIF(COUNT(DISTINCT s.strain_id), 0), 
        2
    ) as completion_percentage
FROM lysobacter.tests t
JOIN lysobacter.test_categories tc ON t.category_id = tc.category_id
CROSS JOIN lysobacter.strains s
LEFT JOIN lysobacter.test_results_boolean trb ON t.test_id = trb.test_id AND s.strain_id = trb.strain_id
LEFT JOIN lysobacter.test_results_numeric trn ON t.test_id = trn.test_id AND s.strain_id = trn.strain_id
LEFT JOIN lysobacter.test_results_text trt ON t.test_id = trt.test_id AND s.strain_id = trt.strain_id
WHERE t.is_active = TRUE AND s.is_active = TRUE
GROUP BY t.test_id, t.test_name, t.test_type, tc.category_name
ORDER BY tc.category_name, t.test_name;

-- Strain data completeness
CREATE VIEW lysobacter.v_strain_completeness AS
SELECT 
    s.strain_id,
    s.strain_identifier,
    s.scientific_name,
    COUNT(DISTINCT t.test_id) as total_available_tests,
    COUNT(DISTINCT CASE 
        WHEN t.test_type = 'boolean' THEN trb.test_id
        WHEN t.test_type = 'numeric' THEN trn.test_id
        WHEN t.test_type = 'text' THEN trt.test_id
    END) as completed_tests,
    ROUND(
        COUNT(DISTINCT CASE 
            WHEN t.test_type = 'boolean' THEN trb.test_id
            WHEN t.test_type = 'numeric' THEN trn.test_id
            WHEN t.test_type = 'text' THEN trt.test_id
        END) * 100.0 / NULLIF(COUNT(DISTINCT t.test_id), 0), 
        2
    ) as completeness_percentage
FROM lysobacter.strains s
CROSS JOIN lysobacter.tests t
LEFT JOIN lysobacter.test_results_boolean trb ON s.strain_id = trb.strain_id AND t.test_id = trb.test_id
LEFT JOIN lysobacter.test_results_numeric trn ON s.strain_id = trn.strain_id AND t.test_id = trn.test_id
LEFT JOIN lysobacter.test_results_text trt ON s.strain_id = trt.strain_id AND t.test_id = trt.test_id
WHERE s.is_active = TRUE AND t.is_active = TRUE
GROUP BY s.strain_id, s.strain_identifier, s.scientific_name
ORDER BY completeness_percentage DESC;

-- ========================================
-- SEARCH AND FILTER FUNCTIONS
-- ========================================

-- Function to search strains by criteria with tolerance
CREATE OR REPLACE FUNCTION lysobacter.search_strains_with_tolerance(
    p_criteria JSONB,
    p_tolerance INTEGER DEFAULT 0
)
RETURNS TABLE (
    strain_id INTEGER,
    strain_identifier VARCHAR(100),
    scientific_name VARCHAR(200),
    match_score INTEGER,
    total_criteria INTEGER,
    matching_criteria INTEGER,
    conflicting_criteria INTEGER
) AS $$
DECLARE
    criterion JSONB;
    test_name_key TEXT;
    expected_value TEXT;
    total_criteria_count INTEGER;
BEGIN
    -- Create temporary table for results
    CREATE TEMP TABLE temp_strain_matches (
        strain_id INTEGER,
        match_count INTEGER DEFAULT 0,
        conflict_count INTEGER DEFAULT 0
    );
    
    -- Initialize with all strains
    INSERT INTO temp_strain_matches (strain_id)
    SELECT s.strain_id FROM lysobacter.strains s WHERE s.is_active = TRUE;
    
    -- Count total criteria
    total_criteria_count := jsonb_array_length(p_criteria);
    
    -- Process each criterion
    FOR criterion IN SELECT jsonb_array_elements(p_criteria)
    LOOP
        test_name_key := criterion->>'test_name';
        expected_value := criterion->>'expected_value';
        
        -- Update matches for boolean tests
        UPDATE temp_strain_matches 
        SET match_count = match_count + 1
        WHERE strain_id IN (
            SELECT trb.strain_id
            FROM lysobacter.test_results_boolean trb
            JOIN lysobacter.tests t ON trb.test_id = t.test_id
            JOIN lysobacter.test_values tv ON trb.value_id = tv.value_id
            WHERE t.test_code = test_name_key 
            AND tv.value_code = expected_value
        );
        
        -- Update conflicts for boolean tests
        UPDATE temp_strain_matches 
        SET conflict_count = conflict_count + 1
        WHERE strain_id IN (
            SELECT trb.strain_id
            FROM lysobacter.test_results_boolean trb
            JOIN lysobacter.tests t ON trb.test_id = t.test_id
            JOIN lysobacter.test_values tv ON trb.value_id = tv.value_id
            WHERE t.test_code = test_name_key 
            AND tv.value_code != expected_value
            AND tv.value_code != 'n.d.'
        );
    END LOOP;
    
    -- Return results within tolerance
    RETURN QUERY
    SELECT 
        s.strain_id,
        s.strain_identifier,
        s.scientific_name,
        tsm.match_count as match_score,
        total_criteria_count as total_criteria,
        tsm.match_count as matching_criteria,
        tsm.conflict_count as conflicting_criteria
    FROM temp_strain_matches tsm
    JOIN lysobacter.strains s ON tsm.strain_id = s.strain_id
    WHERE tsm.conflict_count <= p_tolerance
    ORDER BY tsm.match_count DESC, tsm.conflict_count ASC;
    
    -- Clean up
    DROP TABLE temp_strain_matches;
END;
$$ LANGUAGE plpgsql;

-- Function to get strain test profile
CREATE OR REPLACE FUNCTION lysobacter.get_strain_test_profile(p_strain_id INTEGER)
RETURNS TABLE (
    category_name VARCHAR(100),
    test_name VARCHAR(150),
    test_type VARCHAR(20),
    result_value TEXT,
    confidence_level VARCHAR(20),
    tested_date DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        tc.category_name,
        t.test_name,
        t.test_type,
        CASE 
            WHEN t.test_type = 'boolean' THEN tv.value_name
            WHEN t.test_type = 'numeric' THEN 
                trn.value_type || ': ' || trn.numeric_value::text || 
                COALESCE(' ' || trn.measurement_unit, '')
            WHEN t.test_type = 'text' THEN trt.text_value
        END as result_value,
        COALESCE(trb.confidence_level, trn.confidence_level, trt.confidence_level) as confidence_level,
        COALESCE(trb.tested_date, trn.tested_date, trt.tested_date) as tested_date
    FROM lysobacter.tests t
    JOIN lysobacter.test_categories tc ON t.category_id = tc.category_id
    LEFT JOIN lysobacter.test_results_boolean trb ON t.test_id = trb.test_id AND trb.strain_id = p_strain_id
    LEFT JOIN lysobacter.test_values tv ON trb.value_id = tv.value_id
    LEFT JOIN lysobacter.test_results_numeric trn ON t.test_id = trn.test_id AND trn.strain_id = p_strain_id
    LEFT JOIN lysobacter.test_results_text trt ON t.test_id = trt.test_id AND trt.strain_id = p_strain_id
    WHERE (trb.result_id IS NOT NULL OR trn.result_id IS NOT NULL OR trt.result_id IS NOT NULL)
    AND t.is_active = TRUE
    ORDER BY tc.sort_order, t.sort_order;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- DATA VALIDATION FUNCTIONS
-- ========================================

-- Function to validate strain data consistency
CREATE OR REPLACE FUNCTION lysobacter.validate_strain_data()
RETURNS TABLE (
    validation_type VARCHAR(50),
    strain_id INTEGER,
    strain_identifier VARCHAR(100),
    issue_description TEXT
) AS $$
BEGIN
    -- Check for strains without any test results
    RETURN QUERY
    SELECT 
        'NO_TEST_RESULTS'::VARCHAR(50),
        s.strain_id,
        s.strain_identifier,
        'Strain has no test results recorded'::TEXT
    FROM lysobacter.strains s
    WHERE s.is_active = TRUE
    AND NOT EXISTS (
        SELECT 1 FROM lysobacter.test_results_boolean trb WHERE trb.strain_id = s.strain_id
        UNION
        SELECT 1 FROM lysobacter.test_results_numeric trn WHERE trn.strain_id = s.strain_id
        UNION
        SELECT 1 FROM lysobacter.test_results_text trt WHERE trt.strain_id = s.strain_id
    );
    
    -- Check for inconsistent numeric ranges
    RETURN QUERY
    SELECT 
        'INVALID_NUMERIC_RANGE'::VARCHAR(50),
        s.strain_id,
        s.strain_identifier,
        'Invalid numeric range: minimum > maximum for test: ' || t.test_name
    FROM lysobacter.strains s
    JOIN lysobacter.test_results_numeric trn_min ON s.strain_id = trn_min.strain_id AND trn_min.value_type = 'minimum'
    JOIN lysobacter.test_results_numeric trn_max ON s.strain_id = trn_max.strain_id AND trn_max.value_type = 'maximum'
    JOIN lysobacter.tests t ON trn_min.test_id = t.test_id AND trn_max.test_id = t.test_id
    WHERE trn_min.numeric_value > trn_max.numeric_value;
    
    -- Check for duplicate test results
    RETURN QUERY
    SELECT 
        'DUPLICATE_BOOLEAN_RESULTS'::VARCHAR(50),
        s.strain_id,
        s.strain_identifier,
        'Duplicate boolean test results for test: ' || t.test_name
    FROM lysobacter.strains s
    JOIN lysobacter.test_results_boolean trb ON s.strain_id = trb.strain_id
    JOIN lysobacter.tests t ON trb.test_id = t.test_id
    GROUP BY s.strain_id, s.strain_identifier, t.test_name, trb.test_id
    HAVING COUNT(*) > 1;
    
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- BULK OPERATIONS
-- ========================================

-- Function to bulk import strain data
CREATE OR REPLACE FUNCTION lysobacter.bulk_import_strain_results(
    p_strain_identifier VARCHAR(100),
    p_test_results JSONB
)
RETURNS BOOLEAN AS $$
DECLARE
    v_strain_id INTEGER;
    test_result JSONB;
    v_test_id INTEGER;
    v_value_id INTEGER;
BEGIN
    -- Get strain ID
    SELECT strain_id INTO v_strain_id 
    FROM lysobacter.strains 
    WHERE strain_identifier = p_strain_identifier AND is_active = TRUE;
    
    IF v_strain_id IS NULL THEN
        RAISE EXCEPTION 'Strain not found: %', p_strain_identifier;
    END IF;
    
    -- Process each test result
    FOR test_result IN SELECT jsonb_array_elements(p_test_results)
    LOOP
        -- Get test ID
        SELECT test_id INTO v_test_id
        FROM lysobacter.tests
        WHERE test_code = test_result->>'test_code' AND is_active = TRUE;
        
        IF v_test_id IS NULL THEN
            CONTINUE; -- Skip unknown tests
        END IF;
        
        -- Handle boolean results
        IF test_result->>'test_type' = 'boolean' THEN
            SELECT value_id INTO v_value_id
            FROM lysobacter.test_values
            WHERE test_id = v_test_id AND value_code = test_result->>'value';
            
            IF v_value_id IS NOT NULL THEN
                INSERT INTO lysobacter.test_results_boolean 
                (strain_id, test_id, value_id, notes, confidence_level)
                VALUES (v_strain_id, v_test_id, v_value_id, 
                       test_result->>'notes', 
                       COALESCE(test_result->>'confidence_level', 'high'))
                ON CONFLICT (strain_id, test_id) 
                DO UPDATE SET 
                    value_id = EXCLUDED.value_id,
                    notes = EXCLUDED.notes,
                    confidence_level = EXCLUDED.confidence_level,
                    updated_at = CURRENT_TIMESTAMP;
            END IF;
            
        -- Handle numeric results
        ELSIF test_result->>'test_type' = 'numeric' THEN
            INSERT INTO lysobacter.test_results_numeric 
            (strain_id, test_id, value_type, numeric_value, measurement_unit, notes, confidence_level)
            VALUES (v_strain_id, v_test_id, 
                   test_result->>'value_type',
                   (test_result->>'numeric_value')::DECIMAL,
                   test_result->>'measurement_unit',
                   test_result->>'notes', 
                   COALESCE(test_result->>'confidence_level', 'high'))
            ON CONFLICT (strain_id, test_id, value_type) 
            DO UPDATE SET 
                numeric_value = EXCLUDED.numeric_value,
                measurement_unit = EXCLUDED.measurement_unit,
                notes = EXCLUDED.notes,
                confidence_level = EXCLUDED.confidence_level,
                updated_at = CURRENT_TIMESTAMP;
                
        -- Handle text results
        ELSIF test_result->>'test_type' = 'text' THEN
            INSERT INTO lysobacter.test_results_text 
            (strain_id, test_id, text_value, notes, confidence_level)
            VALUES (v_strain_id, v_test_id, 
                   test_result->>'text_value',
                   test_result->>'notes', 
                   COALESCE(test_result->>'confidence_level', 'high'))
            ON CONFLICT (strain_id, test_id) 
            DO UPDATE SET 
                text_value = EXCLUDED.text_value,
                notes = EXCLUDED.notes,
                confidence_level = EXCLUDED.confidence_level,
                updated_at = CURRENT_TIMESTAMP;
        END IF;
    END LOOP;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql; 