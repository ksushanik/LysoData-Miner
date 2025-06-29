-- Lysobacter Database Schema (3NF Compliant)
-- Created for managing lysobacter bacterial strains and their properties

CREATE SCHEMA IF NOT EXISTS lysobacter;

-- ========================================
-- REFERENCE TABLES (Dictionaries)
-- ========================================

-- Test categories for grouping related parameters
CREATE TABLE lysobacter.test_categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Individual tests/parameters that can be performed
CREATE TABLE lysobacter.tests (
    test_id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES lysobacter.test_categories(category_id),
    test_name VARCHAR(150) NOT NULL,
    test_code VARCHAR(50) UNIQUE, -- Short code for API/import
    test_type VARCHAR(20) NOT NULL CHECK (test_type IN ('boolean', 'numeric', 'text')),
    description TEXT,
    measurement_unit VARCHAR(20), -- For numeric tests (°C, pH, etc.)
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category_id, test_name)
);

-- Possible values for boolean/categorical tests
CREATE TABLE lysobacter.test_values (
    value_id SERIAL PRIMARY KEY,
    test_id INTEGER NOT NULL REFERENCES lysobacter.tests(test_id) ON DELETE CASCADE,
    value_code VARCHAR(10) NOT NULL, -- '+', '-', '+/-', 'n.d.'
    value_name VARCHAR(50) NOT NULL, -- 'Positive', 'Negative', 'Intermediate', 'No Data'
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(test_id, value_code)
);

-- Sources of strain data (laboratories, publications, etc.)
CREATE TABLE lysobacter.data_sources (
    source_id SERIAL PRIMARY KEY,
    source_name VARCHAR(200) NOT NULL,
    source_type VARCHAR(50), -- 'laboratory', 'publication', 'database'
    contact_info TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Collection numbers/identifiers
CREATE TABLE lysobacter.collection_numbers (
    collection_number_id SERIAL PRIMARY KEY,
    collection_code VARCHAR(50) NOT NULL, -- DSM, ATCC, etc.
    collection_number VARCHAR(100) NOT NULL,
    collection_name VARCHAR(200),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(collection_code, collection_number)
);

-- ========================================
-- MAIN ENTITIES
-- ========================================

-- Main strains table
CREATE TABLE lysobacter.strains (
    strain_id SERIAL PRIMARY KEY,
    strain_identifier VARCHAR(100) NOT NULL UNIQUE, -- Main strain ID
    scientific_name VARCHAR(200),
    common_name VARCHAR(200),
    description TEXT,
    isolation_source TEXT,
    isolation_location TEXT,
    isolation_date DATE,
    source_id INTEGER REFERENCES lysobacter.data_sources(source_id),
    gc_content_min DECIMAL(5,2), -- GC content percentage
    gc_content_max DECIMAL(5,2),
    gc_content_optimal DECIMAL(5,2),
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Link strains to collection numbers (many-to-many)
CREATE TABLE lysobacter.strain_collections (
    strain_id INTEGER NOT NULL REFERENCES lysobacter.strains(strain_id) ON DELETE CASCADE,
    collection_number_id INTEGER NOT NULL REFERENCES lysobacter.collection_numbers(collection_number_id),
    is_primary BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (strain_id, collection_number_id)
);

-- ========================================
-- TEST RESULTS
-- ========================================

-- Boolean/categorical test results
CREATE TABLE lysobacter.test_results_boolean (
    result_id SERIAL PRIMARY KEY,
    strain_id INTEGER NOT NULL REFERENCES lysobacter.strains(strain_id) ON DELETE CASCADE,
    test_id INTEGER NOT NULL REFERENCES lysobacter.tests(test_id),
    value_id INTEGER NOT NULL REFERENCES lysobacter.test_values(value_id),
    notes TEXT,
    confidence_level VARCHAR(20) DEFAULT 'high', -- 'high', 'medium', 'low'
    tested_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(strain_id, test_id)
);

-- Numeric test results (temperature, pH, etc.)
CREATE TABLE lysobacter.test_results_numeric (
    result_id SERIAL PRIMARY KEY,
    strain_id INTEGER NOT NULL REFERENCES lysobacter.strains(strain_id) ON DELETE CASCADE,
    test_id INTEGER NOT NULL REFERENCES lysobacter.tests(test_id),
    value_type VARCHAR(20) NOT NULL CHECK (value_type IN ('minimum', 'maximum', 'optimal', 'single')),
    numeric_value DECIMAL(10,4) NOT NULL,
    measurement_unit VARCHAR(20),
    notes TEXT,
    confidence_level VARCHAR(20) DEFAULT 'high',
    tested_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(strain_id, test_id, value_type)
);

-- Text-based test results (for free-form data)
CREATE TABLE lysobacter.test_results_text (
    result_id SERIAL PRIMARY KEY,
    strain_id INTEGER NOT NULL REFERENCES lysobacter.strains(strain_id) ON DELETE CASCADE,
    test_id INTEGER NOT NULL REFERENCES lysobacter.tests(test_id),
    text_value TEXT NOT NULL,
    notes TEXT,
    confidence_level VARCHAR(20) DEFAULT 'high',
    tested_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(strain_id, test_id)
);

-- ========================================
-- AUDIT AND HISTORY
-- ========================================

-- Audit trail for changes
CREATE TABLE lysobacter.audit_log (
    log_id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER NOT NULL,
    operation VARCHAR(20) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- INDEXES FOR PERFORMANCE
-- ========================================

-- Strains indexes
CREATE INDEX idx_strains_identifier ON lysobacter.strains(strain_identifier);
CREATE INDEX idx_strains_source ON lysobacter.strains(source_id);
CREATE INDEX idx_strains_active ON lysobacter.strains(is_active);

-- Tests indexes
CREATE INDEX idx_tests_category ON lysobacter.tests(category_id);
CREATE INDEX idx_tests_type ON lysobacter.tests(test_type);
CREATE INDEX idx_tests_active ON lysobacter.tests(is_active);

-- Test results indexes
CREATE INDEX idx_results_boolean_strain ON lysobacter.test_results_boolean(strain_id);
CREATE INDEX idx_results_boolean_test ON lysobacter.test_results_boolean(test_id);
CREATE INDEX idx_results_numeric_strain ON lysobacter.test_results_numeric(strain_id);
CREATE INDEX idx_results_numeric_test ON lysobacter.test_results_numeric(test_id);
CREATE INDEX idx_results_text_strain ON lysobacter.test_results_text(strain_id);

-- Full-text search indexes
CREATE INDEX idx_strains_text_search ON lysobacter.strains USING gin(
    to_tsvector('english', coalesce(strain_identifier, '') || ' ' || 
                          coalesce(scientific_name, '') || ' ' || 
                          coalesce(description, ''))
);

-- ========================================
-- TRIGGERS FOR AUDIT
-- ========================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION lysobacter.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_strains_updated_at 
    BEFORE UPDATE ON lysobacter.strains 
    FOR EACH ROW EXECUTE FUNCTION lysobacter.update_updated_at_column();

CREATE TRIGGER update_results_boolean_updated_at 
    BEFORE UPDATE ON lysobacter.test_results_boolean 
    FOR EACH ROW EXECUTE FUNCTION lysobacter.update_updated_at_column();

CREATE TRIGGER update_results_numeric_updated_at 
    BEFORE UPDATE ON lysobacter.test_results_numeric 
    FOR EACH ROW EXECUTE FUNCTION lysobacter.update_updated_at_column();

-- ========================================
-- VIEWS FOR COMMON QUERIES
-- ========================================

-- Complete strain information view
CREATE VIEW lysobacter.v_strains_complete AS
SELECT 
    s.strain_id,
    s.strain_identifier,
    s.scientific_name,
    s.common_name,
    s.description,
    s.isolation_source,
    s.isolation_location,
    s.isolation_date,
    ds.source_name,
    ds.source_type,
    s.gc_content_min,
    s.gc_content_max,
    s.gc_content_optimal,
    s.notes,
    s.is_active,
    s.created_at,
    s.updated_at,
    -- Collection numbers as array
    ARRAY_AGG(
        CASE 
            WHEN cn.collection_code IS NOT NULL 
            THEN cn.collection_code || ' ' || cn.collection_number 
            ELSE NULL 
        END
    ) FILTER (WHERE cn.collection_code IS NOT NULL) AS collection_numbers
FROM lysobacter.strains s
LEFT JOIN lysobacter.data_sources ds ON s.source_id = ds.source_id
LEFT JOIN lysobacter.strain_collections sc ON s.strain_id = sc.strain_id
LEFT JOIN lysobacter.collection_numbers cn ON sc.collection_number_id = cn.collection_number_id
GROUP BY s.strain_id, ds.source_name, ds.source_type;

-- Test results summary view
CREATE VIEW lysobacter.v_test_results_summary AS
SELECT 
    s.strain_id,
    s.strain_identifier,
    tc.category_name,
    t.test_name,
    t.test_type,
    t.measurement_unit,
    -- Boolean results
    CASE 
        WHEN t.test_type = 'boolean' THEN tv.value_name
        ELSE NULL
    END AS boolean_result,
    -- Numeric results
    CASE 
        WHEN t.test_type = 'numeric' THEN 
            CASE trn.value_type
                WHEN 'minimum' THEN 'Min: ' || trn.numeric_value::text
                WHEN 'maximum' THEN 'Max: ' || trn.numeric_value::text
                WHEN 'optimal' THEN 'Opt: ' || trn.numeric_value::text
                ELSE trn.numeric_value::text
            END
        ELSE NULL
    END AS numeric_result,
    -- Text results
    CASE 
        WHEN t.test_type = 'text' THEN trt.text_value
        ELSE NULL
    END AS text_result,
    COALESCE(trb.confidence_level, trn.confidence_level, trt.confidence_level) AS confidence_level,
    COALESCE(trb.tested_date, trn.tested_date, trt.tested_date) AS tested_date
FROM lysobacter.strains s
CROSS JOIN lysobacter.tests t
JOIN lysobacter.test_categories tc ON t.category_id = tc.category_id
LEFT JOIN lysobacter.test_results_boolean trb ON s.strain_id = trb.strain_id AND t.test_id = trb.test_id
LEFT JOIN lysobacter.test_values tv ON trb.value_id = tv.value_id
LEFT JOIN lysobacter.test_results_numeric trn ON s.strain_id = trn.strain_id AND t.test_id = trn.test_id
LEFT JOIN lysobacter.test_results_text trt ON s.strain_id = trt.strain_id AND t.test_id = trt.test_id
WHERE s.is_active = TRUE AND t.is_active = TRUE
    AND (trb.result_id IS NOT NULL OR trn.result_id IS NOT NULL OR trt.result_id IS NOT NULL); 