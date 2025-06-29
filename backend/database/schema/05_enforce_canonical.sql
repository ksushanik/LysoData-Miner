-- Enforce canonical tests
-- Prevent insertion of tests with codes not present in canonical list YAML (via canonical_tests table)

-- Helper table populated from YAML sync script
CREATE TABLE IF NOT EXISTS lysobacter.canonical_test_codes (
    test_code VARCHAR(50) PRIMARY KEY
);

-- Populate from current canonical tests (idempotent)
INSERT INTO lysobacter.canonical_test_codes (test_code)
SELECT test_code FROM lysobacter.tests WHERE is_active = TRUE
ON CONFLICT DO NOTHING;

-- Trigger function
CREATE OR REPLACE FUNCTION lysobacter.check_canonical_test()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM lysobacter.canonical_test_codes WHERE test_code = NEW.test_code
    ) THEN
        RAISE EXCEPTION 'Test code % is not canonical', NEW.test_code;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger
DROP TRIGGER IF EXISTS trg_check_canonical_test ON lysobacter.tests;
CREATE CONSTRAINT TRIGGER trg_check_canonical_test
AFTER INSERT OR UPDATE OF test_code ON lysobacter.tests
FOR EACH ROW EXECUTE FUNCTION lysobacter.check_canonical_test(); 