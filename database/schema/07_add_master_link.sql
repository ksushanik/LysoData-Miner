-- Add master_strain_id to link duplicates to their master record
ALTER TABLE lysobacter.strains
ADD COLUMN master_strain_id INTEGER REFERENCES lysobacter.strains(strain_id) ON DELETE SET NULL;

-- Add an index for faster lookups of duplicates by their master
CREATE INDEX idx_strains_master_strain_id ON lysobacter.strains(master_strain_id);

-- Add a comment to explain the new fields
COMMENT ON COLUMN lysobacter.strains.is_duplicate IS 'True if this strain is a synonym/duplicate of another master strain.';
COMMENT ON COLUMN lysobacter.strains.master_strain_id IS 'If this is a duplicate, points to the strain_id of the master record.'; 