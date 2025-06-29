-- Migration: rename category 'biochemical_other' to 'other_biochemical'
-- Date: 2025-07-08
-- Author: AI assistant

BEGIN;

-- 1. Обновляем имя категории
UPDATE lysobacter.test_categories
SET category_name = 'other_biochemical'
WHERE category_name = 'biochemical_other';

-- 2. Убеждаемся, что не возникает дубликата (если категория уже была создана ранее)
-- Если существует дубликат, переносим тесты и удаляем лишнюю запись
DO $$
DECLARE
    old_id INT;
    new_id INT;
BEGIN
    SELECT category_id INTO old_id FROM lysobacter.test_categories WHERE category_name = 'biochemical_other' LIMIT 1;
    SELECT category_id INTO new_id FROM lysobacter.test_categories WHERE category_name = 'other_biochemical' LIMIT 1;

    IF old_id IS NOT NULL AND new_id IS NOT NULL AND old_id <> new_id THEN
        -- Перемещаем тесты на правильную категорию
        UPDATE lysobacter.tests SET category_id = new_id WHERE category_id = old_id;
        -- Удаляем дубликат категории
        DELETE FROM lysobacter.test_categories WHERE category_id = old_id;
    END IF;
END $$;

COMMIT; 