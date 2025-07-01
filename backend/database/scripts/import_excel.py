#!/usr/bin/env python3
"""
Excel Import Script for Lysobacter Database

This script imports strain data and test results from Excel files into the Lysobacter database.
Supports both strain metadata and test results in structured Excel format.
"""

import pandas as pd
import psycopg2
import psycopg2.extras
import argparse
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

class LysobacterImporter:
    """Main class for importing Excel data into Lysobacter database."""
    
    def __init__(self, db_config: Dict[str, str]):
        """Initialize with database configuration."""
        self.db_config = db_config
        self.conn = None
        self.test_cache = {}
        self.test_value_cache = {}
        
    def connect(self):
        """Connect to PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.conn.autocommit = False
            print("✓ Connected to database")
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            sys.exit(1)
    
    def disconnect(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            print("✓ Database connection closed")
    
    def load_test_cache(self):
        """Load tests and test values into cache for performance."""
        print("Loading test configuration cache...")
        
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Load tests
            cur.execute("""
                SELECT t.test_id, t.test_code, t.test_name, t.test_type, tc.category_name
                FROM lysobacter.tests t
                JOIN lysobacter.test_categories tc ON t.category_id = tc.category_id
                WHERE t.is_active = TRUE
            """)
            
            for row in cur.fetchall():
                self.test_cache[row['test_code']] = dict(row)
            
            # Load test values for boolean tests
            cur.execute("""
                SELECT tv.test_id, tv.value_id, tv.value_code, tv.value_name
                FROM lysobacter.test_values tv
                JOIN lysobacter.tests t ON tv.test_id = t.test_id
                WHERE t.test_type = 'boolean'
            """)
            
            for row in cur.fetchall():
                test_id = row['test_id']
                if test_id not in self.test_value_cache:
                    self.test_value_cache[test_id] = {}
                self.test_value_cache[test_id][row['value_code']] = {
                    'value_id': row['value_id'],
                    'value_name': row['value_name']
                }
        
        print(f"✓ Loaded {len(self.test_cache)} tests")
    
    def import_strains(self, excel_file: str, sheet_name: str = 'Strains') -> List[int]:
        """Import strain metadata from Excel file."""
        print(f"Importing strains from {excel_file}, sheet: {sheet_name}")
        
        try:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
        except Exception as e:
            print(f"✗ Error reading Excel file: {e}")
            return []
        
        # Validate required columns
        required_columns = ['strain_identifier']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"✗ Missing required columns: {missing_columns}")
            return []
        
        strain_ids = []
        
        with self.conn.cursor() as cur:
            for index, row in df.iterrows():
                try:
                    # Prepare strain data
                    strain_data = {
                        'strain_identifier': row.get('strain_identifier'),
                        'scientific_name': row.get('scientific_name'),
                        'common_name': row.get('common_name'),
                        'description': row.get('description'),
                        'isolation_source': row.get('isolation_source'),
                        'isolation_location': row.get('isolation_location'),
                        'isolation_date': self._parse_date(row.get('isolation_date')),
                        'notes': row.get('notes')
                    }
                    
                    # Remove None values
                    strain_data = {k: v for k, v in strain_data.items() if pd.notna(v)}
                    
                    # Insert strain
                    columns = ', '.join(strain_data.keys())
                    placeholders = ', '.join(['%s'] * len(strain_data))
                    
                    cur.execute(f"""
                        INSERT INTO lysobacter.strains ({columns})
                        VALUES ({placeholders})
                        ON CONFLICT (strain_identifier) 
                        DO UPDATE SET 
                            scientific_name = EXCLUDED.scientific_name,
                            common_name = EXCLUDED.common_name,
                            description = EXCLUDED.description,
                            isolation_source = EXCLUDED.isolation_source,
                            isolation_location = EXCLUDED.isolation_location,
                            isolation_date = EXCLUDED.isolation_date,
                            notes = EXCLUDED.notes,
                            updated_at = CURRENT_TIMESTAMP
                        RETURNING strain_id
                    """, list(strain_data.values()))
                    
                    strain_id = cur.fetchone()[0]
                    strain_ids.append(strain_id)
                    
                    print(f"✓ Imported strain: {strain_data['strain_identifier']} (ID: {strain_id})")
                    
                except Exception as e:
                    print(f"✗ Error importing strain at row {index + 2}: {e}")
                    continue
        
        self.conn.commit()
        print(f"✓ Imported {len(strain_ids)} strains")
        return strain_ids
    
    def import_test_results(self, excel_file: str, sheet_name: str = 'TestResults') -> int:
        """Import test results from Excel file."""
        print(f"Importing test results from {excel_file}, sheet: {sheet_name}")
        
        try:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
        except Exception as e:
            print(f"✗ Error reading Excel file: {e}")
            return 0
        
        # Validate required columns
        required_columns = ['strain_identifier', 'test_code', 'result_value']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"✗ Missing required columns: {missing_columns}")
            return 0
        
        results_imported = 0
        
        with self.conn.cursor() as cur:
            for index, row in df.iterrows():
                try:
                    strain_identifier = row['strain_identifier']
                    test_code = row['test_code']
                    result_value = row['result_value']
                    
                    # Skip rows with missing required data
                    if pd.isna(strain_identifier) or pd.isna(test_code) or pd.isna(result_value):
                        continue
                    
                    # Get strain ID
                    cur.execute(
                        "SELECT strain_id FROM lysobacter.strains WHERE strain_identifier = %s",
                        (strain_identifier,)
                    )
                    strain_result = cur.fetchone()
                    if not strain_result:
                        print(f"✗ Strain not found: {strain_identifier}")
                        continue
                    
                    strain_id = strain_result[0]
                    
                    # Get test info
                    if test_code not in self.test_cache:
                        print(f"✗ Test not found: {test_code}")
                        continue
                    
                    test_info = self.test_cache[test_code]
                    test_id = test_info['test_id']
                    test_type = test_info['test_type']
                    
                    # Prepare common fields
                    common_fields = {
                        'notes': row.get('notes'),
                        'confidence_level': row.get('confidence_level', 'high'),
                        'tested_date': self._parse_date(row.get('tested_date'))
                    }
                    
                    # Import based on test type
                    if test_type == 'boolean':
                        self._import_boolean_result(cur, strain_id, test_id, result_value, common_fields)
                    elif test_type == 'numeric':
                        self._import_numeric_result(cur, strain_id, test_id, result_value, row, common_fields)
                    elif test_type == 'text':
                        self._import_text_result(cur, strain_id, test_id, result_value, common_fields)
                    
                    results_imported += 1
                    
                except Exception as e:
                    print(f"✗ Error importing result at row {index + 2}: {e}")
                    continue
        
        self.conn.commit()
        print(f"✓ Imported {results_imported} test results")
        return results_imported
    
    def _import_boolean_result(self, cursor, strain_id: int, test_id: int, result_value: str, common_fields: Dict):
        """Import boolean test result."""
        # Normalize result value
        result_value = str(result_value).strip()
        
        # Map common variations
        value_mapping = {
            'positive': '+', 'pos': '+', 'yes': '+', 'true': '+', '1': '+',
            'negative': '-', 'neg': '-', 'no': '-', 'false': '-', '0': '-',
            'intermediate': '+/-', 'variable': '+/-', 'weak': '+/-',
            'no data': 'n.d.', 'nd': 'n.d.', 'unknown': 'n.d.', '': 'n.d.'
        }
        
        normalized_value = value_mapping.get(result_value.lower(), result_value)
        
        # Get value ID
        if test_id not in self.test_value_cache:
            print(f"✗ No values configured for test ID {test_id}")
            return
        
        if normalized_value not in self.test_value_cache[test_id]:
            print(f"✗ Invalid boolean value '{result_value}' for test ID {test_id}")
            return
        
        value_id = self.test_value_cache[test_id][normalized_value]['value_id']
        
        # Insert result
        cursor.execute("""
            INSERT INTO lysobacter.test_results_boolean 
            (strain_id, test_id, value_id, notes, confidence_level, tested_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (strain_id, test_id) 
            DO UPDATE SET 
                value_id = EXCLUDED.value_id,
                notes = EXCLUDED.notes,
                confidence_level = EXCLUDED.confidence_level,
                tested_date = EXCLUDED.tested_date,
                updated_at = CURRENT_TIMESTAMP
        """, (strain_id, test_id, value_id, common_fields['notes'], 
              common_fields['confidence_level'], common_fields['tested_date']))
    
    def _import_numeric_result(self, cursor, strain_id: int, test_id: int, result_value: str, row: pd.Series, common_fields: Dict):
        """Import numeric test result."""
        # Handle different numeric formats
        value_type = row.get('value_type', 'single')
        measurement_unit = row.get('measurement_unit')
        
        try:
            # Parse numeric value
            numeric_value = float(str(result_value).replace(',', '.'))
            
            cursor.execute("""
                INSERT INTO lysobacter.test_results_numeric 
                (strain_id, test_id, value_type, numeric_value, measurement_unit, notes, confidence_level, tested_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (strain_id, test_id, value_type) 
                DO UPDATE SET 
                    numeric_value = EXCLUDED.numeric_value,
                    measurement_unit = EXCLUDED.measurement_unit,
                    notes = EXCLUDED.notes,
                    confidence_level = EXCLUDED.confidence_level,
                    tested_date = EXCLUDED.tested_date,
                    updated_at = CURRENT_TIMESTAMP
            """, (strain_id, test_id, value_type, numeric_value, measurement_unit,
                  common_fields['notes'], common_fields['confidence_level'], common_fields['tested_date']))
                  
        except ValueError:
            print(f"✗ Invalid numeric value: {result_value}")
    
    def _import_text_result(self, cursor, strain_id: int, test_id: int, result_value: str, common_fields: Dict):
        """Import text test result."""
        cursor.execute("""
            INSERT INTO lysobacter.test_results_text 
            (strain_id, test_id, text_value, notes, confidence_level, tested_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (strain_id, test_id) 
            DO UPDATE SET 
                text_value = EXCLUDED.text_value,
                notes = EXCLUDED.notes,
                confidence_level = EXCLUDED.confidence_level,
                tested_date = EXCLUDED.tested_date,
                updated_at = CURRENT_TIMESTAMP
        """, (strain_id, test_id, str(result_value), common_fields['notes'], 
              common_fields['confidence_level'], common_fields['tested_date']))
    
    def _parse_date(self, date_value) -> Optional[str]:
        """Parse date from various formats."""
        if pd.isna(date_value):
            return None
            
        if isinstance(date_value, datetime):
            return date_value.strftime('%Y-%m-%d')
            
        if isinstance(date_value, str):
            # Try common date formats
            formats = ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%m/%d/%Y']
            for fmt in formats:
                try:
                    return datetime.strptime(date_value, fmt).strftime('%Y-%m-%d')
                except ValueError:
                    continue
        
        return None
    
    def generate_template(self, output_file: str):
        """Generate Excel template for data import."""
        print(f"Generating Excel template: {output_file}")
        
        # Strains template
        strains_data = {
            'strain_identifier': ['LYS-001', 'LYS-002', 'LYS-003'],
            'scientific_name': ['Lysobacter antibioticus', 'Lysobacter enzymogenes', 'Lysobacter brunescens'],
            'common_name': ['Antibiotic-producing lysobacter', 'Enzyme-producing lysobacter', 'Brown-pigmented lysobacter'],
            'description': ['Example strain 1', 'Example strain 2', 'Example strain 3'],
            'isolation_source': ['Soil', 'Forest soil', 'Lake sediment'],
            'isolation_location': ['Moscow region', 'Leningrad region', 'Baikal region'],
            'isolation_date': ['2023-01-15', '2023-02-20', '2023-03-10'],
            'notes': ['Primary research strain', 'High enzyme activity', 'Brown pigmentation']
        }
        
        # Test results template
        test_results_data = {
            'strain_identifier': ['LYS-001', 'LYS-001', 'LYS-001', 'LYS-002', 'LYS-002'],
            'test_code': ['temperature', 'temperature', 'catalase', 'ph_level'],
            'result_value': ['+', '25.0', '37.0', '+', '7.5'],
            'value_type': ['', 'optimal', 'maximum', '', 'optimal'],
            'measurement_unit': ['', '°C', '°C', '', 'pH'],
            'notes': ['Clear spore formation', 'Optimal temperature', 'Maximum temperature', 'Positive catalase', 'Optimal pH'],
            'confidence_level': ['high', 'high', 'high', 'high', 'medium'],
            'tested_date': ['2023-01-20', '2023-01-30', '2023-01-30', '2023-03-01', '2023-03-07']
        }
        
        # Create Excel file with multiple sheets
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            pd.DataFrame(strains_data).to_excel(writer, sheet_name='Strains', index=False)
            pd.DataFrame(test_results_data).to_excel(writer, sheet_name='TestResults', index=False)
            
            # Add test codes reference
            if self.test_cache:
                test_codes_data = {
                    'test_code': [code for code in self.test_cache.keys()],
                    'test_name': [info['test_name'] for info in self.test_cache.values()],
                    'test_type': [info['test_type'] for info in self.test_cache.values()],
                    'category': [info['category_name'] for info in self.test_cache.values()]
                }
                pd.DataFrame(test_codes_data).to_excel(writer, sheet_name='TestCodes', index=False)
        
        print(f"✓ Template generated: {output_file}")


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description='Import Lysobacter data from Excel files')
    parser.add_argument('--excel-file', required=True, help='Path to Excel file')
    parser.add_argument('--strains-sheet', default='Strains', help='Sheet name for strains data')
    parser.add_argument('--results-sheet', default='TestResults', help='Sheet name for test results')
    parser.add_argument('--import-strains', action='store_true', help='Import strains data')
    parser.add_argument('--import-results', action='store_true', help='Import test results')
    parser.add_argument('--generate-template', help='Generate Excel template file')
    parser.add_argument('--db-host', default='localhost', help='Database host')
    parser.add_argument('--db-port', default='5432', help='Database port')
    parser.add_argument('--db-name', default='lysobacter_db', help='Database name')
    parser.add_argument('--db-user', default='lysobacter_user', help='Database user')
    parser.add_argument('--db-password', default='lysobacter_password', help='Database password')
    
    args = parser.parse_args()
    
    # Database configuration
    db_config = {
        'host': args.db_host,
        'port': args.db_port,
        'database': args.db_name,
        'user': args.db_user,
        'password': args.db_password
    }
    
    # Initialize importer
    importer = LysobacterImporter(db_config)
    
    try:
        importer.connect()
        importer.load_test_cache()
        
        # Generate template
        if args.generate_template:
            importer.generate_template(args.generate_template)
            return
        
        # Check if Excel file exists
        if not os.path.exists(args.excel_file):
            print(f"✗ Excel file not found: {args.excel_file}")
            sys.exit(1)
        
        # Import strains
        if args.import_strains:
            strain_ids = importer.import_strains(args.excel_file, args.strains_sheet)
            print(f"✓ Imported {len(strain_ids)} strains")
        
        # Import test results
        if args.import_results:
            results_count = importer.import_test_results(args.excel_file, args.results_sheet)
            print(f"✓ Imported {results_count} test results")
        
        if not args.import_strains and not args.import_results:
            print("✗ No import action specified. Use --import-strains and/or --import-results")
            
    except Exception as e:
        print(f"✗ Import failed: {e}")
        sys.exit(1)
    finally:
        importer.disconnect()


if __name__ == '__main__':
    main() 