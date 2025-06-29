-- Add is_duplicate flag to strains table
-- This allows marking strains that are duplicates of a master strain

ALTER TABLE lysobacter.strains
ADD COLUMN is_duplicate BOOLEAN NOT NULL DEFAULT FALSE;

-- Add an index for faster lookups of duplicates
CREATE INDEX idx_strains_is_duplicate ON lysobacter.strains(is_duplicate); 