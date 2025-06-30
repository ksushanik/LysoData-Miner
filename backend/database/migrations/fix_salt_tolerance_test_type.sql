-- Fix Salt Tolerance test type from boolean to numeric
-- This migration changes the test type and adds proper measurement unit

BEGIN;

-- Update the test type and add measurement unit
UPDATE lysobacter.tests 
SET 
    test_type = 'numeric',
    measurement_unit = '% NaCl',
    description = 'Salt tolerance range (% NaCl)'
WHERE test_name = 'Солеустойчивость' 
   OR test_name = 'Salt Tolerance'
   OR test_id = 5;

-- Remove any existing boolean test results for this test FIRST (to avoid foreign key constraint)
DELETE FROM lysobacter.test_results_boolean 
WHERE test_id = (SELECT test_id FROM lysobacter.tests WHERE test_name = 'Солеустойчивость' LIMIT 1);

-- Remove any existing boolean test values for this test (if any)
DELETE FROM lysobacter.test_values 
WHERE test_id = (SELECT test_id FROM lysobacter.tests WHERE test_name = 'Солеустойчивость' LIMIT 1);

COMMIT;

-- Verify the change
SELECT test_id, test_name, test_type, measurement_unit, description 
FROM lysobacter.tests 
WHERE test_name = 'Солеустойчивость' OR test_name = 'Salt Tolerance'; 