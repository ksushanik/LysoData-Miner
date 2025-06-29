-- Sample data for testing Lysobacter database functionality
-- This file contains example strains and test results for validation

-- ========================================
-- SAMPLE STRAINS
-- ========================================

-- Insert sample strains
INSERT INTO lysobacter.strains (
    strain_identifier, 
    scientific_name, 
    common_name,
    description,
    isolation_source,
    isolation_location,
    isolation_date,
    source_id,
    notes
) VALUES 
(
    'LYS-001',
    'Lysobacter antibioticus',
    'Antibiotic-producing lysobacter',
    'Strain isolated from agricultural soil with strong antibiotic activity',
    'Agricultural soil',
    'Moscow region, Russia',
    '2023-01-15',
    (SELECT source_id FROM lysobacter.data_sources WHERE source_name = 'Laboratory Research Data'),
    'Primary research strain for antibiotic studies'
),
(
    'LYS-002', 
    'Lysobacter enzymogenes',
    'Enzyme-producing lysobacter',
    'Strain with high enzymatic activity, particularly cellulase production',
    'Forest soil',
    'Leningrad region, Russia', 
    '2023-02-20',
    (SELECT source_id FROM lysobacter.data_sources WHERE source_name = 'Laboratory Research Data'),
    'High cellulase activity observed'
),
(
    'LYS-003',
    'Lysobacter brunescens',
    'Brown-pigmented lysobacter',
    'Strain characterized by brown pigment production',
    'Lake sediment',
    'Baikal region, Russia',
    '2023-03-10',
    (SELECT source_id FROM lysobacter.data_sources WHERE source_name = 'Literature Review'),
    'Notable for brown pigmentation'
);

-- Add collection numbers for strains
INSERT INTO lysobacter.strain_collections (strain_id, collection_number_id, is_primary, notes)
SELECT 
    s.strain_id,
    cn.collection_number_id,
    TRUE,
    'Primary collection deposit'
FROM lysobacter.strains s
CROSS JOIN lysobacter.collection_numbers cn
WHERE s.strain_identifier = 'LYS-001' AND cn.collection_code = 'DSM'
UNION ALL
SELECT 
    s.strain_id,
    cn.collection_number_id,
    FALSE,
    'Secondary collection deposit'
FROM lysobacter.strains s
CROSS JOIN lysobacter.collection_numbers cn
WHERE s.strain_identifier = 'LYS-002' AND cn.collection_code = 'ATCC';

-- ========================================
-- SAMPLE BOOLEAN TEST RESULTS
-- ========================================

-- Helper function to get test and value IDs
DO $$
DECLARE
    strain_lys001_id INTEGER;
    strain_lys002_id INTEGER;
    strain_lys003_id INTEGER;
BEGIN
    -- Get strain IDs
    SELECT strain_id INTO strain_lys001_id FROM lysobacter.strains WHERE strain_identifier = 'LYS-001';
    SELECT strain_id INTO strain_lys002_id FROM lysobacter.strains WHERE strain_identifier = 'LYS-002'; 
    SELECT strain_id INTO strain_lys003_id FROM lysobacter.strains WHERE strain_identifier = 'LYS-003';

    -- LYS-001 test results
    INSERT INTO lysobacter.test_results_boolean (strain_id, test_id, value_id, notes, confidence_level, tested_date) VALUES
    -- Morphological tests
    (strain_lys001_id, 
     (SELECT test_id FROM lysobacter.tests WHERE test_code = 'spore_formation'),
     (SELECT value_id FROM lysobacter.test_values tv JOIN lysobacter.tests t ON tv.test_id = t.test_id WHERE t.test_code = 'spore_formation' AND tv.value_code = '+'),
     'Clear spore formation observed under microscopy', 'high', '2023-01-20'),
    
    (strain_lys001_id,
     (SELECT test_id FROM lysobacter.tests WHERE test_code = 'motility'),
     (SELECT value_id FROM lysobacter.test_values tv JOIN lysobacter.tests t ON tv.test_id = t.test_id WHERE t.test_code = 'motility' AND tv.value_code = '+'),
     'Active motility observed in liquid medium', 'high', '2023-01-20'),

    -- Physiological tests
    (strain_lys001_id,
     (SELECT test_id FROM lysobacter.tests WHERE test_code = 'salt_tolerance'),
     (SELECT value_id FROM lysobacter.test_values tv JOIN lysobacter.tests t ON tv.test_id = t.test_id WHERE t.test_code = 'salt_tolerance' AND tv.value_code = '+'),
     'Growth observed up to 3% NaCl', 'high', '2023-01-22'),

    -- Biochemical enzyme tests
    (strain_lys001_id,
     (SELECT test_id FROM lysobacter.tests WHERE test_code = 'proteolytic_activity'),
     (SELECT value_id FROM lysobacter.test_values tv JOIN lysobacter.tests t ON tv.test_id = t.test_id WHERE t.test_code = 'proteolytic_activity' AND tv.value_code = '+'),
     'Strong proteolytic activity on casein plates', 'high', '2023-01-25'),

    (strain_lys001_id,
     (SELECT test_id FROM lysobacter.tests WHERE test_code = 'catalase'),
     (SELECT value_id FROM lysobacter.test_values tv JOIN lysobacter.tests t ON tv.test_id = t.test_id WHERE t.test_code = 'catalase' AND tv.value_code = '+'),
     'Positive catalase reaction', 'high', '2023-01-25'),

    (strain_lys001_id,
     (SELECT test_id FROM lysobacter.tests WHERE test_code = 'oxidase'),
     (SELECT value_id FROM lysobacter.test_values tv JOIN lysobacter.tests t ON tv.test_id = t.test_id WHERE t.test_code = 'oxidase' AND tv.value_code = '-'),
     'Negative oxidase test', 'high', '2023-01-25'),

    -- Sugar utilization tests  
    (strain_lys001_id,
     (SELECT test_id FROM lysobacter.tests WHERE test_code = 'glucose_fermentation'),
     (SELECT value_id FROM lysobacter.test_values tv JOIN lysobacter.tests t ON tv.test_id = t.test_id WHERE t.test_code = 'glucose_fermentation' AND tv.value_code = '+'),
     'Glucose fermentation positive', 'high', '2023-01-28'),

    (strain_lys001_id,
     (SELECT test_id FROM lysobacter.tests WHERE test_code = 'maltose'),
     (SELECT value_id FROM lysobacter.test_values tv JOIN lysobacter.tests t ON tv.test_id = t.test_id WHERE t.test_code = 'maltose' AND tv.value_code = '+'),
     'Maltose utilization positive', 'medium', '2023-01-30'),

    (strain_lys001_id,
     (SELECT test_id FROM lysobacter.tests WHERE test_code = 'lactose'),
     (SELECT value_id FROM lysobacter.test_values tv JOIN lysobacter.tests t ON tv.test_id = t.test_id WHERE t.test_code = 'lactose' AND tv.value_code = '-'),
     'No lactose utilization', 'high', '2023-01-30');

    -- LYS-002 test results (different pattern)
    INSERT INTO lysobacter.test_results_boolean (strain_id, test_id, value_id, notes, confidence_level, tested_date) VALUES
    -- Morphological tests
    (strain_lys002_id,
     (SELECT test_id FROM lysobacter.tests WHERE test_code = 'spore_formation'),
     (SELECT value_id FROM lysobacter.test_values tv JOIN lysobacter.tests t ON tv.test_id = t.test_id WHERE t.test_code = 'spore_formation' AND tv.value_code = '-'),
     'No spore formation observed', 'high', '2023-02-25'),

    (strain_lys002_id,
     (SELECT test_id FROM lysobacter.tests WHERE test_code = 'motility'),
     (SELECT value_id FROM lysobacter.test_values tv JOIN lysobacter.tests t ON tv.test_id = t.test_id WHERE t.test_code = 'motility' AND tv.value_code = '+/-'),
     'Weak motility, variable results', 'medium', '2023-02-25'),

    -- Enzyme activity
    (strain_lys002_id,
     (SELECT test_id FROM lysobacter.tests WHERE test_code = 'cellulase_activity'),
     (SELECT value_id FROM lysobacter.test_values tv JOIN lysobacter.tests t ON tv.test_id = t.test_id WHERE t.test_code = 'cellulase_activity' AND tv.value_code = '+'),
     'Very high cellulase activity', 'high', '2023-03-01'),

    (strain_lys002_id,
     (SELECT test_id FROM lysobacter.tests WHERE test_code = 'catalase'),
     (SELECT value_id FROM lysobacter.test_values tv JOIN lysobacter.tests t ON tv.test_id = t.test_id WHERE t.test_code = 'catalase' AND tv.value_code = '+'),
     'Positive catalase reaction', 'high', '2023-03-01');

    -- LYS-003 test results (some missing data)
    INSERT INTO lysobacter.test_results_boolean (strain_id, test_id, value_id, notes, confidence_level, tested_date) VALUES
    (strain_lys003_id,
     (SELECT test_id FROM lysobacter.tests WHERE test_code = 'spore_formation'),
     (SELECT value_id FROM lysobacter.test_values tv JOIN lysobacter.tests t ON tv.test_id = t.test_id WHERE t.test_code = 'spore_formation' AND tv.value_code = 'n.d.'),
     'Data not available from literature source', 'low', '2023-03-15'),

    (strain_lys003_id,
     (SELECT test_id FROM lysobacter.tests WHERE test_code = 'catalase'),
     (SELECT value_id FROM lysobacter.test_values tv JOIN lysobacter.tests t ON tv.test_id = t.test_id WHERE t.test_code = 'catalase' AND tv.value_code = '+'),
     'Positive catalase from literature', 'medium', '2023-03-15');

END $$;

-- ========================================
-- SAMPLE NUMERIC TEST RESULTS
-- ========================================

DO $$
DECLARE
    strain_lys001_id INTEGER;
    strain_lys002_id INTEGER;
    strain_lys003_id INTEGER;
    temp_test_id INTEGER;
    ph_test_id INTEGER;
BEGIN
    -- Get strain and test IDs
    SELECT strain_id INTO strain_lys001_id FROM lysobacter.strains WHERE strain_identifier = 'LYS-001';
    SELECT strain_id INTO strain_lys002_id FROM lysobacter.strains WHERE strain_identifier = 'LYS-002';
    SELECT strain_id INTO strain_lys003_id FROM lysobacter.strains WHERE strain_identifier = 'LYS-003';
    SELECT test_id INTO temp_test_id FROM lysobacter.tests WHERE test_code = 'temperature';
    SELECT test_id INTO ph_test_id FROM lysobacter.tests WHERE test_code = 'ph_level';

    -- Temperature ranges for LYS-001
    INSERT INTO lysobacter.test_results_numeric (strain_id, test_id, value_type, numeric_value, measurement_unit, notes, confidence_level, tested_date) VALUES
    (strain_lys001_id, temp_test_id, 'minimum', 5.0, '°C', 'No growth below 5°C', 'high', '2023-01-30'),
    (strain_lys001_id, temp_test_id, 'maximum', 37.0, '°C', 'No growth above 37°C', 'high', '2023-01-30'),
    (strain_lys001_id, temp_test_id, 'optimal', 25.0, '°C', 'Optimal growth at 25°C', 'high', '2023-01-30'),

    -- pH ranges for LYS-001
    (strain_lys001_id, ph_test_id, 'minimum', 6.0, 'pH', 'Minimum pH for growth', 'high', '2023-02-01'),
    (strain_lys001_id, ph_test_id, 'maximum', 9.0, 'pH', 'Maximum pH for growth', 'high', '2023-02-01'),
    (strain_lys001_id, ph_test_id, 'optimal', 7.5, 'pH', 'Optimal pH for growth', 'high', '2023-02-01'),

    -- Temperature ranges for LYS-002 (different profile)
    (strain_lys002_id, temp_test_id, 'minimum', 10.0, '°C', 'Minimum growth temperature', 'high', '2023-03-05'),
    (strain_lys002_id, temp_test_id, 'maximum', 35.0, '°C', 'Maximum growth temperature', 'high', '2023-03-05'),
    (strain_lys002_id, temp_test_id, 'optimal', 28.0, '°C', 'Optimal temperature for enzymes', 'high', '2023-03-05'),

    -- pH ranges for LYS-002  
    (strain_lys002_id, ph_test_id, 'minimum', 5.5, 'pH', 'Acid-tolerant strain', 'medium', '2023-03-07'),
    (strain_lys002_id, ph_test_id, 'maximum', 8.5, 'pH', 'Upper pH limit', 'medium', '2023-03-07'),
    (strain_lys002_id, ph_test_id, 'optimal', 7.0, 'pH', 'Neutral pH optimal', 'high', '2023-03-07'),

    -- Limited data for LYS-003 (only optimal values)
    (strain_lys003_id, temp_test_id, 'optimal', 30.0, '°C', 'From literature data', 'low', '2023-03-20'),
    (strain_lys003_id, ph_test_id, 'optimal', 7.2, 'pH', 'From literature data', 'low', '2023-03-20');

END $$;

-- ========================================
-- SAMPLE TEXT TEST RESULTS
-- ========================================

DO $$
DECLARE
    strain_lys001_id INTEGER;
    strain_lys002_id INTEGER;
    gc_test_id INTEGER;
BEGIN
    -- Get IDs
    SELECT strain_id INTO strain_lys001_id FROM lysobacter.strains WHERE strain_identifier = 'LYS-001';
    SELECT strain_id INTO strain_lys002_id FROM lysobacter.strains WHERE strain_identifier = 'LYS-002';
    SELECT test_id INTO gc_test_id FROM lysobacter.tests WHERE test_code = 'gc_content';

    -- Add some text-based results
    INSERT INTO lysobacter.test_results_text (strain_id, test_id, text_value, notes, confidence_level, tested_date) VALUES
    (strain_lys001_id, gc_test_id, '68.5% ± 0.5%', 'GC content determined by HPLC analysis', 'high', '2023-02-10'),
    (strain_lys002_id, gc_test_id, '69.2%', 'GC content from genome sequencing', 'high', '2023-03-15');

END $$;

-- ========================================
-- VALIDATION QUERIES
-- ========================================

-- Check data insertion
SELECT 
    'Strains created' as description,
    COUNT(*) as count
FROM lysobacter.strains 
WHERE strain_identifier LIKE 'LYS-%'

UNION ALL

SELECT 
    'Boolean results' as description,
    COUNT(*) as count
FROM lysobacter.test_results_boolean trb
JOIN lysobacter.strains s ON trb.strain_id = s.strain_id
WHERE s.strain_identifier LIKE 'LYS-%'

UNION ALL

SELECT 
    'Numeric results' as description,
    COUNT(*) as count
FROM lysobacter.test_results_numeric trn
JOIN lysobacter.strains s ON trn.strain_id = s.strain_id
WHERE s.strain_identifier LIKE 'LYS-%'

UNION ALL

SELECT 
    'Text results' as description,
    COUNT(*) as count
FROM lysobacter.test_results_text trt
JOIN lysobacter.strains s ON trt.strain_id = s.strain_id
WHERE s.strain_identifier LIKE 'LYS-%';

-- Sample search query - find strains with spore formation and catalase positive
SELECT 
    'Search demo: Spore+ and Catalase+' as description,
    COUNT(*) as matching_strains
FROM lysobacter.search_strains_with_tolerance(
    '[
        {"test_name": "spore_formation", "expected_value": "+"},
        {"test_name": "catalase", "expected_value": "+"}
    ]'::jsonb,
    0
);

-- Show strain completeness
SELECT 
    strain_identifier,
    completeness_percentage,
    completed_tests,
    total_available_tests
FROM lysobacter.v_strain_completeness
WHERE strain_identifier LIKE 'LYS-%'
ORDER BY completeness_percentage DESC; 