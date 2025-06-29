# Database Design Documentation
# Lysobacter Strain Collection Database

## Overview

This document describes the database design for the Lysobacter bacterial strain collection system. The database is designed to comply with Third Normal Form (3NF) requirements and supports comprehensive management of strain information and test results.

## Design Principles

### 1. Third Normal Form Compliance

The database strictly adheres to 3NF principles:

- **1NF**: All attributes are atomic, no repeating groups
- **2NF**: No partial dependencies on composite keys
- **3NF**: No transitive dependencies between non-key attributes

### 2. Separation of Concerns

- **Reference Data**: Normalized into separate lookup tables
- **Core Entities**: Main business objects (strains)
- **Test Results**: Separated by data type (boolean, numeric, text)
- **Audit Trail**: Complete change history

### 3. Extensibility

- New test types can be added without schema changes
- Category-based organization allows for grouping
- Flexible result storage supports various data types

## Schema Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  test_categories│    │      tests       │    │   test_values   │
│                 │    │                  │    │                 │
│ - category_id   │───▶│ - test_id        │───▶│ - value_id      │
│ - category_name │    │ - category_id    │    │ - test_id       │
│ - description   │    │ - test_name      │    │ - value_code    │
│ - sort_order    │    │ - test_code      │    │ - value_name    │
└─────────────────┘    │ - test_type      │    └─────────────────┘
                       │ - description    │
                       │ - unit           │
                       └──────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐
│     strains     │    │  test_results_*  │
│                 │    │                  │
│ - strain_id     │◀───│ - result_id      │
│ - identifier    │    │ - strain_id      │
│ - scientific_nm │    │ - test_id        │
│ - common_name   │    │ - value/result   │
│ - description   │    │ - confidence     │
│ - isolation_*   │    │ - tested_date    │
│ - notes         │    └──────────────────┘
└─────────────────┘
```

## Table Specifications

### Reference Tables

#### test_categories
Purpose: Group related tests into logical categories
```sql
test_categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    sort_order INTEGER DEFAULT 0
)
```

**Categories:**
- `morphological` - Morphological properties
- `physiological` - Physiological properties  
- `biochemical_enzymes` - Enzyme activities
- `biochemical_breakdown` - Breakdown capabilities
- `biochemical_utilization` - Sugar utilization
- `biochemical_other` - Other biochemical tests

#### tests
Purpose: Define individual test parameters
```sql
tests (
    test_id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES test_categories,
    test_name VARCHAR(150) NOT NULL,
    test_code VARCHAR(50) UNIQUE,
    test_type VARCHAR(20) CHECK (test_type IN ('boolean', 'numeric', 'text')),
    description TEXT,
    measurement_unit VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0
)
```

**Test Types:**
- `boolean` - Yes/No/Intermediate results (+, -, +/-, n.d.)
- `numeric` - Numerical values with min/max/optimal ranges
- `text` - Free-form text results

#### test_values
Purpose: Define possible values for boolean tests
```sql
test_values (
    value_id SERIAL PRIMARY KEY,
    test_id INTEGER REFERENCES tests,
    value_code VARCHAR(10) NOT NULL,  -- '+', '-', '+/-', 'n.d.'
    value_name VARCHAR(50) NOT NULL,  -- 'Positive', 'Negative', etc.
    description TEXT,
    sort_order INTEGER DEFAULT 0
)
```

### Core Entity Tables

#### strains
Purpose: Store bacterial strain information
```sql
strains (
    strain_id SERIAL PRIMARY KEY,
    strain_identifier VARCHAR(100) NOT NULL UNIQUE,
    scientific_name VARCHAR(200),
    common_name VARCHAR(200),
    description TEXT,
    isolation_source TEXT,
    isolation_location TEXT,
    isolation_date DATE,
    source_id INTEGER REFERENCES data_sources,
    gc_content_min DECIMAL(5,2),
    gc_content_max DECIMAL(5,2),
    gc_content_optimal DECIMAL(5,2),
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Test Result Tables

#### test_results_boolean
Purpose: Store boolean test results
```sql
test_results_boolean (
    result_id SERIAL PRIMARY KEY,
    strain_id INTEGER REFERENCES strains,
    test_id INTEGER REFERENCES tests,
    value_id INTEGER REFERENCES test_values,
    notes TEXT,
    confidence_level VARCHAR(20) DEFAULT 'high',
    tested_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(strain_id, test_id)
)
```

#### test_results_numeric
Purpose: Store numerical test results
```sql
test_results_numeric (
    result_id SERIAL PRIMARY KEY,
    strain_id INTEGER REFERENCES strains,
    test_id INTEGER REFERENCES tests,
    value_type VARCHAR(20) CHECK (value_type IN ('minimum', 'maximum', 'optimal', 'single')),
    numeric_value DECIMAL(10,4) NOT NULL,
    measurement_unit VARCHAR(20),
    notes TEXT,
    confidence_level VARCHAR(20) DEFAULT 'high',
    tested_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(strain_id, test_id, value_type)
)
```

#### test_results_text
Purpose: Store text-based test results
```sql
test_results_text (
    result_id SERIAL PRIMARY KEY,
    strain_id INTEGER REFERENCES strains,
    test_id INTEGER REFERENCES tests,
    text_value TEXT NOT NULL,
    notes TEXT,
    confidence_level VARCHAR(20) DEFAULT 'high',
    tested_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(strain_id, test_id)
)
```

## Normalization Analysis

### First Normal Form (1NF)
✅ **Achieved**
- All attributes contain atomic values
- No repeating groups or arrays in single columns
- Each row is uniquely identifiable

### Second Normal Form (2NF)  
✅ **Achieved**
- All non-key attributes are fully functionally dependent on primary keys
- No partial dependencies exist
- Composite keys properly designed

### Third Normal Form (3NF)
✅ **Achieved**
- No transitive dependencies between non-key attributes
- Test categories separated from tests
- Test values normalized into separate table
- Data sources and collection numbers are independent entities

## Indexing Strategy

### Primary Indexes
```sql
-- Primary keys (automatic)
-- Foreign key indexes (automatic)

-- Performance indexes
CREATE INDEX idx_strains_identifier ON lysobacter.strains(strain_identifier);
CREATE INDEX idx_strains_source ON lysobacter.strains(source_id);
CREATE INDEX idx_strains_active ON lysobacter.strains(is_active);

CREATE INDEX idx_tests_category ON lysobacter.tests(category_id);
CREATE INDEX idx_tests_type ON lysobacter.tests(test_type);
CREATE INDEX idx_tests_active ON lysobacter.tests(is_active);

CREATE INDEX idx_results_boolean_strain ON lysobacter.test_results_boolean(strain_id);
CREATE INDEX idx_results_boolean_test ON lysobacter.test_results_boolean(test_id);
CREATE INDEX idx_results_numeric_strain ON lysobacter.test_results_numeric(strain_id);
CREATE INDEX idx_results_numeric_test ON lysobacter.test_results_numeric(test_id);
```

### Full-Text Search
```sql
CREATE INDEX idx_strains_text_search ON lysobacter.strains USING gin(
    to_tsvector('english', 
        coalesce(strain_identifier, '') || ' ' || 
        coalesce(scientific_name, '') || ' ' || 
        coalesce(description, '')
    )
);
```

## Views and Functions

### Key Views

#### v_strains_complete
Comprehensive strain information with collection numbers
```sql
CREATE VIEW lysobacter.v_strains_complete AS
SELECT 
    s.*,
    ds.source_name,
    ds.source_type,
    ARRAY_AGG(cn.collection_code || ' ' || cn.collection_number) 
        FILTER (WHERE cn.collection_code IS NOT NULL) AS collection_numbers
FROM lysobacter.strains s
LEFT JOIN lysobacter.data_sources ds ON s.source_id = ds.source_id
LEFT JOIN lysobacter.strain_collections sc ON s.strain_id = sc.strain_id
LEFT JOIN lysobacter.collection_numbers cn ON sc.collection_number_id = cn.collection_number_id
GROUP BY s.strain_id, ds.source_name, ds.source_type;
```

#### v_test_results_summary
Unified view of all test results
```sql
-- Shows boolean, numeric, and text results in unified format
-- Includes confidence levels and test dates
-- Organized by category and test type
```

### Key Functions

#### search_strains_with_tolerance()
Advanced search with configurable tolerance for non-matching criteria
```sql
SELECT * FROM lysobacter.search_strains_with_tolerance(
    '[{"test_name": "spore_formation", "expected_value": "+"},
      {"test_name": "catalase", "expected_value": "+"}]'::jsonb,
    1  -- Allow 1 non-matching criterion
);
```

#### get_strain_test_profile()
Complete test profile for a specific strain
```sql
SELECT * FROM lysobacter.get_strain_test_profile(strain_id);
```

#### validate_strain_data()
Data integrity validation
```sql
SELECT * FROM lysobacter.validate_strain_data();
```

## Data Types and Constraints

### Confidence Levels
- `high` - Reliable, well-documented results
- `medium` - Good quality, some uncertainty
- `low` - Literature data, uncertain quality

### Value Types (Numeric)
- `minimum` - Lower bound of range
- `maximum` - Upper bound of range  
- `optimal` - Optimal value
- `single` - Single measurement

### Test Value Codes (Boolean)
- `+` - Positive result
- `-` - Negative result
- `+/-` - Intermediate/Variable result
- `n.d.` - No data available

## Performance Considerations

### Query Optimization
1. **Proper indexing** on foreign keys and search columns
2. **View materialization** for frequently accessed complex queries
3. **Partitioning strategy** for large result tables (future consideration)

### Scalability Features
1. **Horizontal partitioning** ready for test results tables
2. **Archive strategy** for historical data
3. **Bulk import functions** for large datasets

## Security and Audit

### Audit Trail
- Complete change history in `audit_log` table
- Automatic timestamping with triggers
- User tracking capability

### Data Integrity
- Foreign key constraints ensure referential integrity
- Check constraints validate data ranges
- Unique constraints prevent duplicates
- NOT NULL constraints ensure required data

## Migration Strategy

### Version Control
- Sequential numbered migration files
- Rollback procedures for each migration
- Dependency tracking between migrations

### Backup Strategy
- Regular automated backups
- Point-in-time recovery capability
- Test data restoration procedures

## Future Enhancements

### Planned Features
1. **Genomic data integration** (sequences, annotations)
2. **Image storage** (microscopy, colony photos)
3. **Experiment protocols** (detailed methodology)
4. **User management** (access control, permissions)
5. **API endpoints** (REST/GraphQL interface)

### Scalability Improvements
1. **Read replicas** for analytics workloads
2. **Caching layer** (Redis/Memcached)
3. **Search engine** (Elasticsearch) for complex queries
4. **Data warehouse** for reporting and analytics

## Maintenance Procedures

### Regular Tasks
1. **Index maintenance** (REINDEX, ANALYZE)
2. **Statistics updates** (VACUUM, ANALYZE)
3. **Backup verification** (restore testing)
4. **Data validation** (integrity checks)

### Monitoring
1. **Performance metrics** (query times, index usage)
2. **Growth tracking** (table sizes, record counts)
3. **Error monitoring** (constraint violations, import failures)
4. **Usage analytics** (most queried data, access patterns) 