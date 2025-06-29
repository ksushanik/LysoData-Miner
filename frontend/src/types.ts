export interface TestResult {
    test_name: string;
    result: string;
    category: string;
}

export interface CollectionNumber {
    collection_name: string;
    collection_number: string;
    full_identifier?: string;
}

export interface DataSource {
    source_name: string;
}

export interface StrainData {
    strain_id: number;
    strain_identifier: string;
    scientific_name: string;
    common_name?: string;
    description?: string;
    isolation_source?: string;
    isolation_location?: string;
    isolation_date?: string;
    gc_content_range?: string;
    notes?: string;
    is_active: boolean;
    created_at?: string;
    updated_at?: string;
    data_source?: DataSource;
    collection_numbers?: CollectionNumber[];
}

export interface Strain {
    strain: StrainData;
    test_results: TestResult[];
}

// Типы для системы идентификации
export interface TestCategory {
    category_id: number;
    category_name: string;
    description?: string;
    sort_order?: number;
}

export interface Test {
    test_id: number;
    test_code: string;
    test_name: string;
    test_type: 'boolean' | 'numeric' | 'text';
    description?: string;
    measurement_unit?: string;
    category_id: number;
    category_name?: string;
    sort_order?: number;
    is_active?: boolean;
}

// Типы для числовых значений тестов
export interface NumericTestValue {
    exact?: number;
    range?: {
        min: number;
        max: number;
    };
    mode: 'exact' | 'range';
}

// Типы для булевых значений тестов
export interface BooleanTestValue {
    value: '+' | '-' | '+/-' | 'n.d.';
}

// Объединенный тип для значений тестов
export interface TestValue {
    test_id: number;
    test_code: string;
    test_type: 'boolean' | 'numeric' | 'text';
    test_name?: string;
    measurement_unit?: string;
    boolean_value?: BooleanTestValue;
    numeric_value?: NumericTestValue;
    text_value?: string;
}

// Запрос на идентификацию
export interface IdentificationRequest {
    test_values: TestValue[];
}

// Детали сравнения тестов
export interface MatchDetail {
    test_name: string;
    strain_result?: string;
    query_result: string;
    query_type: string;
    match_status: 'match' | 'partial_match' | 'mismatch' | 'not_found';
}

// Результат идентификации
export interface IdentificationResult {
    strain_id: number;
    strain_identifier: string;
    scientific_name: string;
    common_name?: string;
    isolation_source?: string;
    match_percentage: number;
    matching_tests: number;
    partial_matching_tests: number;
    total_tests: number;
    conflicting_tests: number;
    confidence_score: number;
    details: MatchDetail[];
    data_source?: DataSource;
    collection_numbers?: CollectionNumber[];
}

export interface IdentificationResponse {
    results: IdentificationResult[];
    total_results: number;
    query_summary: {
        total_test_values: number;
        boolean_tests: number;
        numeric_tests: number;
        text_tests: number;
    };
    execution_time_ms: number;
} 