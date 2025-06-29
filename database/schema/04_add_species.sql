/*
04_add_species.sql
Добавляет таблицу species и внешний ключ species_id в strains.
*/

-- ========================================
-- SPECIES REFERENCE TABLE
-- ========================================

CREATE TABLE IF NOT EXISTS lysobacter.species (
    species_id SERIAL PRIMARY KEY,
    scientific_name VARCHAR(200) UNIQUE NOT NULL,
    common_name     VARCHAR(200),
    description     TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TRIGGER для обновления updated_at
CREATE OR REPLACE FUNCTION lysobacter.update_updated_at_species()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_species_updated_at ON lysobacter.species;
CREATE TRIGGER update_species_updated_at
BEFORE UPDATE ON lysobacter.species
FOR EACH ROW EXECUTE FUNCTION lysobacter.update_updated_at_species();

-- ========================================
-- ALTER TABLE strains: добавить species_id
-- ========================================

ALTER TABLE lysobacter.strains
    ADD COLUMN IF NOT EXISTS species_id INTEGER;

ALTER TABLE lysobacter.strains
    ADD CONSTRAINT IF NOT EXISTS strains_species_fk
        FOREIGN KEY (species_id) REFERENCES lysobacter.species(species_id);

-- Индекс для быстрого поиска по виду
CREATE INDEX IF NOT EXISTS idx_strains_species ON lysobacter.strains(species_id);

-- ========================================
-- МИГРАЦИЯ СУЩЕСТВУЮЩИХ ДАННЫХ
-- ========================================
-- Создаём записи видов, которых ещё нет, и связываем их со штаммами
INSERT INTO lysobacter.species (scientific_name)
SELECT DISTINCT scientific_name FROM lysobacter.strains
WHERE scientific_name IS NOT NULL
ON CONFLICT (scientific_name) DO NOTHING;

UPDATE lysobacter.strains s
SET species_id = sp.species_id
FROM lysobacter.species sp
WHERE s.scientific_name = sp.scientific_name
  AND s.species_id IS NULL;
-- ======================================== 