-- Migration: Remove spore formation test for Lysobacter
-- Reason: All Lysobacter are non-spore-forming gram-negative rods
-- Date: 2025-07-01

-- Begin transaction
BEGIN;

-- Save test_id for reference
DO $$
DECLARE
    spore_test_id INTEGER;
BEGIN
    -- Get test_id for spore_formation
    SELECT test_id INTO spore_test_id 
    FROM lysobacter.tests 
    WHERE test_code = 'spore_formation';
    
    -- Remove test results from all results tables
    IF spore_test_id IS NOT NULL THEN
        -- Remove boolean results
        DELETE FROM lysobacter.test_results_boolean 
        WHERE test_id = spore_test_id;
        
        -- Remove numeric results (if any)
        DELETE FROM lysobacter.test_results_numeric 
        WHERE test_id = spore_test_id;
        
        -- Remove text results (if any)
        DELETE FROM lysobacter.test_results_text 
        WHERE test_id = spore_test_id;
        
        -- Remove the test itself
        DELETE FROM lysobacter.tests 
        WHERE test_id = spore_test_id;
        
        RAISE NOTICE 'Removed spore_formation test (ID: %) and all associated results', spore_test_id;
    ELSE
        RAISE NOTICE 'spore_formation test not found, nothing to remove';
    END IF;
END
$$;

-- Commit transaction
COMMIT;

-- Verify removal
SELECT 'Remaining tests in morphological category:' as status;
SELECT t.test_name, t.test_code 
FROM lysobacter.tests t
JOIN lysobacter.test_categories tc ON t.category_id = tc.category_id
WHERE tc.category_name = 'morphological'
ORDER BY t.test_name; 