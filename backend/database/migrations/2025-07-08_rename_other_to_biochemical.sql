-- Migration: rename category 'other_biochemical' to 'biochemical_other'
-- Date: 2025-07-08

BEGIN;
UPDATE lysobacter.test_categories SET category_name='biochemical_other' WHERE category_name='other_biochemical';
COMMIT; 