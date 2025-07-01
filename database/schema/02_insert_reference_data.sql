-- Reference data for Lysobacter database
-- Categories and tests based on the provided requirements

-- ========================================
-- TEST CATEGORIES
-- ========================================

INSERT INTO lysobacter.test_categories (category_name, description, sort_order) VALUES
('morphological', 'Morphological Properties', 1),
('physiological', 'Physiological Properties', 2),
('biochemical_enzymes', 'Biochemical Properties - Enzymes', 3),
('biochemical_breakdown', 'Biochemical Properties - Sugar and Polysaccharide Breakdown', 4),
('biochemical_utilization', 'Biochemical Properties - Sugar Utilization', 5),
('biochemical_other', 'Other Biochemical Characteristics', 6);

-- ========================================
-- MORPHOLOGICAL TESTS
-- ========================================

INSERT INTO lysobacter.tests (category_id, test_name, test_code, test_type, description, sort_order) VALUES
-- Morphological properties (spore_formation removed - all Lysobacter are non-spore-forming)
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'morphological'), 'Motility', 'motility', 'boolean', 'Motility of the organism', 1);

-- ========================================
-- PHYSIOLOGICAL TESTS
-- ========================================

-- Temperature test (numeric with measurement_unit)
INSERT INTO lysobacter.tests (category_id, test_name, test_code, test_type, description, measurement_unit, sort_order) VALUES
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'physiological'), 'Temperature', 'temperature', 'numeric', 'Growth temperature range', '°C', 1);

-- pH test (numeric with measurement_unit)
INSERT INTO lysobacter.tests (category_id, test_name, test_code, test_type, description, measurement_unit, sort_order) VALUES
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'physiological'), 'pH Level', 'ph_level', 'numeric', 'pH range for growth', 'pH', 2);

-- Salt tolerance test (numeric with measurement_unit)
INSERT INTO lysobacter.tests (category_id, test_name, test_code, test_type, description, measurement_unit, sort_order) VALUES
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'physiological'), 'Salt Tolerance', 'salt_tolerance', 'numeric', 'Salt tolerance range (% NaCl)', '%', 3);

-- ========================================
-- BIOCHEMICAL ENZYME TESTS
-- ========================================

INSERT INTO lysobacter.tests (category_id, test_name, test_code, test_type, description, sort_order) VALUES
-- Enzyme tests
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_enzymes'), 'Proteolytic Activity', 'proteolytic_activity', 'boolean', 'Presence of proteolytic enzymes (ability to break down protein components)', 1),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_enzymes'), 'Oxidase', 'oxidase', 'boolean', 'Oxidase enzyme activity', 2),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_enzymes'), 'Catalase', 'catalase', 'boolean', 'Catalase enzyme activity', 3),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_enzymes'), 'Urease', 'urease', 'boolean', 'Urease enzyme activity', 4),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_enzymes'), 'Nitrate Reduction', 'nitrate_reduction', 'boolean', 'Nitrate reduction capability', 5),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_enzymes'), 'Indole Production', 'indole_production', 'boolean', 'Indole production', 6),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_enzymes'), 'Phosphatase', 'phosphatase', 'boolean', 'Phosphatase enzyme activity', 7),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_enzymes'), 'Esterase', 'esterase', 'boolean', 'Esterase enzyme activity', 8),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_enzymes'), 'Cellulase Activity', 'cellulase_activity', 'boolean', 'Cellulase enzyme activity', 9),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_enzymes'), 'Phosphate Solubilization', 'phosphate_solubilization', 'boolean', 'Ability to solubilize phosphates', 10);

-- ========================================
-- BIOCHEMICAL BREAKDOWN TESTS
-- ========================================

INSERT INTO lysobacter.tests (category_id, test_name, test_code, test_type, description, sort_order) VALUES
-- Sugar and polysaccharide breakdown
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_breakdown'), 'Starch Breakdown', 'starch', 'boolean', 'Ability to break down starch', 1),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_breakdown'), 'Aesculin Breakdown', 'aesculin', 'boolean', 'Ability to break down aesculin', 2),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_breakdown'), 'Gelatin Breakdown', 'gelatin', 'boolean', 'Ability to break down gelatin', 3),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_breakdown'), 'Casein Breakdown', 'casein', 'boolean', 'Ability to break down casein', 4),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_breakdown'), 'Tween 20 Breakdown', 'tween_20', 'boolean', 'Ability to break down Tween 20', 5),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_breakdown'), 'Tween 40 Breakdown', 'tween_40', 'boolean', 'Ability to break down Tween 40', 6),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_breakdown'), 'Tween 60 Breakdown', 'tween_60', 'boolean', 'Ability to break down Tween 60', 7),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_breakdown'), 'Chitin Breakdown', 'chitin', 'boolean', 'Ability to break down chitin', 8),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_breakdown'), 'Cellulose Breakdown', 'cellulose', 'boolean', 'Ability to break down cellulose', 9),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_breakdown'), 'Arginine Hydrolase', 'arginine_hydrolase', 'boolean', 'Arginine hydrolase activity', 10),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_breakdown'), 'Pectin Breakdown', 'pectin', 'boolean', 'Ability to break down pectin', 11),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_breakdown'), 'Glucose Fermentation', 'glucose_fermentation', 'boolean', 'Glucose fermentation capability', 12);

-- ========================================
-- BIOCHEMICAL UTILIZATION TESTS
-- ========================================

INSERT INTO lysobacter.tests (category_id, test_name, test_code, test_type, description, sort_order) VALUES
-- Sugar utilization
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_utilization'), 'Maltose Utilization', 'maltose', 'boolean', 'Ability to utilize maltose', 1),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_utilization'), 'Lactose Utilization', 'lactose', 'boolean', 'Ability to utilize lactose', 2),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_utilization'), 'Fructose Utilization', 'fructose', 'boolean', 'Ability to utilize fructose', 3),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_utilization'), 'Arabinose Utilization', 'arabinose', 'boolean', 'Ability to utilize arabinose', 4),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_utilization'), 'Mannose Utilization', 'mannose', 'boolean', 'Ability to utilize mannose', 5),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_utilization'), 'Trehalose Utilization', 'trehalose', 'boolean', 'Ability to utilize trehalose', 6),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_utilization'), 'Sorbitol Utilization', 'sorbitol', 'boolean', 'Ability to utilize sorbitol', 7),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_utilization'), 'Mannitol Utilization', 'mannitol', 'boolean', 'Ability to utilize mannitol', 8),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_utilization'), 'Dextrose Utilization', 'dextrose', 'boolean', 'Ability to utilize dextrose', 9),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_utilization'), 'Xylose Utilization', 'xylose', 'boolean', 'Ability to utilize xylose', 10),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_utilization'), 'Galactose Utilization', 'galactose', 'boolean', 'Ability to utilize galactose', 11),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_utilization'), 'Dulcitol Utilization', 'dulcitol', 'boolean', 'Ability to utilize dulcitol', 12),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_utilization'), 'Cellobiose Utilization', 'cellobiose', 'boolean', 'Ability to utilize cellobiose', 13),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_utilization'), 'Sucrose Utilization', 'sucrose', 'boolean', 'Ability to utilize sucrose', 14),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_utilization'), 'Raffinose Utilization', 'raffinose', 'boolean', 'Ability to utilize raffinose', 15),
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_utilization'), 'Inositol Utilization', 'inositol', 'boolean', 'Ability to utilize inositol', 16);

-- ========================================
-- OTHER BIOCHEMICAL TESTS
-- ========================================

-- GC Content test (numeric with measurement_unit)
INSERT INTO lysobacter.tests (category_id, test_name, test_code, test_type, description, measurement_unit, sort_order) VALUES
((SELECT category_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_other'), 'GC Content', 'gc_content', 'numeric', 'GC content percentage', '%', 1);

-- ========================================
-- TEST VALUES FOR BOOLEAN TESTS
-- ========================================

-- Get all boolean test IDs
DO $$
DECLARE
    test_rec RECORD;
BEGIN
    FOR test_rec IN 
        SELECT test_id FROM lysobacter.tests WHERE test_type = 'boolean'
    LOOP
        -- Insert standard boolean values for each boolean test
        INSERT INTO lysobacter.test_values (test_id, value_code, value_name, description, sort_order) VALUES
        (test_rec.test_id, '+', 'Positive', 'Positive result', 1),
        (test_rec.test_id, '-', 'Negative', 'Negative result', 2),
        (test_rec.test_id, '+/-', 'Intermediate', 'Intermediate/Variable result', 3),
        (test_rec.test_id, 'n.d.', 'No Data', 'No data available', 4);
    END LOOP;
END $$;

-- ========================================
-- SAMPLE DATA SOURCES
-- ========================================

INSERT INTO lysobacter.data_sources (source_name, source_type, contact_info, notes) VALUES
('Laboratory Research Data', 'laboratory', 'Internal laboratory testing', 'Primary research data from laboratory experiments'),
('Literature Review', 'publication', 'Various scientific publications', 'Data collected from published research papers'),
('Culture Collection Database', 'database', 'International culture collections', 'Data from established culture collection databases');

-- ========================================
-- SAMPLE COLLECTION NUMBERS
-- ========================================

INSERT INTO lysobacter.collection_numbers (collection_code, collection_number, collection_name, notes) VALUES
('DSM', 'EXAMPLE-001', 'Deutsche Sammlung von Mikroorganismen', 'Example collection number'),
('ATCC', 'EXAMPLE-001', 'American Type Culture Collection', 'Example collection number'),
('CCUG', 'EXAMPLE-001', 'Culture Collection University of Gothenburg', 'Example collection number'); 