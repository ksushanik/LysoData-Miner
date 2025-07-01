#!/usr/bin/env python3
"""
JSON Import Script for Lysobacter Database

This script imports strain data and test results from JSON files into the Lysobacter database.
JSON format is simpler for LLM processing and provides better structure validation.
"""

import json
import psycopg2
import psycopg2.extras
import argparse
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

class LysobacterJSONImporter:
    """Main class for importing JSON data into Lysobacter database."""
    
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
    
    def validate_json_structure(self, data: Dict) -> bool:
        """Validate basic JSON structure."""
        required_fields = ['metadata', 'strains']
        
        for field in required_fields:
            if field not in data:
                print(f"✗ Missing required field: {field}")
                return False
        
        if not isinstance(data['strains'], list):
            print("✗ 'strains' field must be an array")
            return False
        
        if len(data['strains']) == 0:
            print("✗ 'strains' array is empty")
            return False
        
        # Validate each strain structure
        required_strain_fields = ['strain_identifier']
        
        for i, strain in enumerate(data['strains']):
            for field in required_strain_fields:
                if field not in strain:
                    print(f"✗ Strain {i+1}: Missing required field '{field}'")
                    return False
            
            if 'test_results' in strain and not isinstance(strain['test_results'], list):
                print(f"✗ Strain {i+1}: 'test_results' must be an array")
                return False
        
        print("✓ JSON structure validation passed")
        return True
    
    def import_strain(self, strain_data: Dict) -> Optional[int]:
        """Import single strain into database."""
        try:
            with self.conn.cursor() as cur:
                # -----------------------------
                # Normalization: species table
                # -----------------------------
                species_id_val = None
                scientific_name_val = strain_data.get('scientific_name')
                if scientific_name_val:
                    # Check if species already exists
                    cur.execute("SELECT species_id FROM lysobacter.species WHERE scientific_name = %s", (scientific_name_val,))
                    res = cur.fetchone()
                    if res:
                        species_id_val = res[0]
                    else:
                        # Insert new species
                        cur.execute("INSERT INTO lysobacter.species (scientific_name) VALUES (%s) RETURNING species_id", (scientific_name_val,))
                        species_id_val = cur.fetchone()[0]

                # Prepare strain data - only include non-null values
                strain_fields = {
                    'strain_identifier': strain_data.get('strain_identifier'),
                    'scientific_name': strain_data.get('scientific_name'),
                    'common_name': strain_data.get('common_name'),
                    'description': strain_data.get('description'),
                    'isolation_source': strain_data.get('isolation_source'),
                    'isolation_location': strain_data.get('isolation_location'),
                    'isolation_date': self._parse_date(strain_data.get('isolation_date')),
                    'notes': strain_data.get('notes'),
                    'species_id': species_id_val
                }
                
                # Remove None values
                strain_fields = {k: v for k, v in strain_fields.items() if v is not None}
                
                # Insert strain with conflict handling
                columns = ', '.join(strain_fields.keys())
                placeholders = ', '.join(['%s'] * len(strain_fields))
                
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
                        species_id = EXCLUDED.species_id,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING strain_id
                """, list(strain_fields.values()))
                
                strain_id = cur.fetchone()[0]
                return strain_id
                
        except Exception as e:
            print(f"✗ Error importing strain {strain_data.get('strain_identifier', 'UNKNOWN')}: {e}")
            return None
    
    def import_test_result(self, strain_id: int, strain_identifier: str, test_result: Dict) -> bool:
        """Import single test result."""
        try:
            test_code = test_result.get('test_code')
            if not test_code:
                print(f"✗ Strain {strain_identifier}: Missing test_code")
                return False
            
            if test_code not in self.test_cache:
                print(f"✗ Strain {strain_identifier}: Unknown test code '{test_code}'")
                return False
            
            test_info = self.test_cache[test_code]
            test_id = test_info['test_id']
            test_type = test_info['test_type']
            
            with self.conn.cursor() as cur:
                # Common fields
                common_fields = {
                    'confidence_level': test_result.get('confidence_level', 'high'),
                    'tested_date': self._parse_date(test_result.get('tested_date')),
                    'notes': test_result.get('notes')
                }
                
                if test_type == 'boolean':
                    return self._import_boolean_result(cur, strain_id, test_id, test_result, common_fields)
                elif test_type == 'numeric':
                    return self._import_numeric_result(cur, strain_id, test_id, test_result, common_fields)
                elif test_type == 'text':
                    return self._import_text_result(cur, strain_id, test_id, test_result, common_fields)
                else:
                    print(f"✗ Unknown test type: {test_type}")
                    return False
                    
        except Exception as e:
            print(f"✗ Error importing test result for strain {strain_identifier}: {e}")
            return False
    
    def _import_boolean_result(self, cursor, strain_id: int, test_id: int, test_result: Dict, common_fields: Dict) -> bool:
        """Import boolean test result."""
        result_value = test_result.get('result_value')
        if not result_value:
            print(f"✗ Missing result_value for boolean test")
            return False
        
        # Validate boolean value
        valid_boolean_values = ['+', '-', '+/-', 'n.d.']
        if result_value not in valid_boolean_values:
            print(f"✗ Invalid boolean value '{result_value}'. Must be one of: {valid_boolean_values}")
            return False
        
        # Get value_id
        if test_id not in self.test_value_cache:
            print(f"✗ No boolean values found for test_id {test_id}")
            return False
        
        if result_value not in self.test_value_cache[test_id]:
            print(f"✗ Unknown boolean value '{result_value}' for test_id {test_id}")
            return False
        
        value_id = self.test_value_cache[test_id][result_value]['value_id']
        
        # Insert/update boolean result
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
        """, (strain_id, test_id, value_id, 
              common_fields['notes'], common_fields['confidence_level'], common_fields['tested_date']))
        
        return True
    
    def _import_numeric_result(self, cursor, strain_id: int, test_id: int, test_result: Dict, common_fields: Dict) -> bool:
        """Import numeric test result."""
        result_value = test_result.get('result_value')
        value_type = test_result.get('value_type', 'single')
        measurement_unit = test_result.get('measurement_unit')
        
        if not result_value:
            print(f"✗ Missing result_value for numeric test")
            return False
        
        # Validate numeric value
        try:
            numeric_value = float(result_value)
        except (ValueError, TypeError):
            print(f"✗ Invalid numeric value '{result_value}'")
            return False
        
        # Validate value_type
        valid_value_types = ['minimum', 'maximum', 'optimal', 'single']
        if value_type not in valid_value_types:
            print(f"✗ Invalid value_type '{value_type}'. Must be one of: {valid_value_types}")
            return False
        
        # Insert/update numeric result
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
        
        return True
    
    def _import_text_result(self, cursor, strain_id: int, test_id: int, test_result: Dict, common_fields: Dict) -> bool:
        """Import text test result."""
        text_value = test_result.get('result_value')
        
        if not text_value:
            print(f"✗ Missing result_value for text test")
            return False
        
        # Insert/update text result
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
        """, (strain_id, test_id, text_value,
              common_fields['notes'], common_fields['confidence_level'], common_fields['tested_date']))
        
        return True
    
    def _parse_date(self, date_value) -> Optional[str]:
        """Parse date value to YYYY-MM-DD format."""
        if not date_value:
            return None
        
        # If already string in correct format
        if isinstance(date_value, str):
            try:
                datetime.strptime(date_value, '%Y-%m-%d')
                return date_value
            except ValueError:
                pass
        
        # Try to parse other formats
        date_formats = ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%m/%d/%Y']
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(str(date_value), fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        print(f"✗ Could not parse date: {date_value}")
        return None
    
    def import_from_json(self, json_file: str) -> Dict[str, int]:
        """Import all data from JSON file."""
        print(f"Importing data from {json_file}")
        
        # Load JSON data
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"✗ Error reading JSON file: {e}")
            return {'strains': 0, 'test_results': 0}
        
        # Validate structure
        if not self.validate_json_structure(data):
            return {'strains': 0, 'test_results': 0}
        
        # Print metadata
        metadata = data.get('metadata', {})
        print(f"Source: {metadata.get('source', 'Unknown')}")
        print(f"Expected strains: {metadata.get('total_strains', 'Unknown')}")
        print(f"Expected test results: {metadata.get('total_test_results', 'Unknown')}")
        
        strains_imported = 0
        test_results_imported = 0
        
        try:
            # Import each strain
            for strain_data in data['strains']:
                strain_identifier = strain_data.get('strain_identifier', 'UNKNOWN')
                
                # Import strain
                strain_id = self.import_strain(strain_data)
                if strain_id:
                    strains_imported += 1
                    print(f"✓ Imported strain: {strain_identifier} (ID: {strain_id})")
                    
                    # Import test results for this strain
                    test_results = strain_data.get('test_results', [])
                    for test_result in test_results:
                        if self.import_test_result(strain_id, strain_identifier, test_result):
                            test_results_imported += 1
                else:
                    print(f"✗ Failed to import strain: {strain_identifier}")
            
            # Commit transaction
            self.conn.commit()
            
        except Exception as e:
            print(f"✗ Import failed, rolling back: {e}")
            self.conn.rollback()
            return {'strains': 0, 'test_results': 0}
        
        print(f"✓ Import completed successfully")
        print(f"✓ Strains imported: {strains_imported}")
        print(f"✓ Test results imported: {test_results_imported}")
        
        return {'strains': strains_imported, 'test_results': test_results_imported}
    
    def generate_json_template(self, output_file: str):
        """Generate JSON template file with examples."""
        template = {
            "metadata": {
                "source": "Template file - replace with actual source",
                "created_date": datetime.now().strftime('%Y-%m-%d'),
                "total_strains": 2,
                "total_test_results": 6,
                "notes": "This is a template file showing correct JSON structure"
            },
            "strains": [
                {
                    "strain_identifier": "LYS-TEMPLATE-001",
                    "scientific_name": "Lysobacter enzymogenes",
                    "common_name": "Template strain 1",
                    "description": "Example strain for template demonstration",
                    "isolation_source": "Rhizosphere soil",
                    "isolation_location": "Laboratory example",
                    "isolation_date": "2023-01-01",
                    "notes": "Template strain - replace with real data",
                    "test_results": [

                        {
                            "test_code": "motility",
                            "result_value": "+",
                            "test_type": "boolean",
                            "value_type": None,
                            "measurement_unit": None,
                            "confidence_level": "high",
                            "tested_date": "2023-01-02",
                            "notes": "Motile bacteria"
                        },
                        {
                            "test_code": "temperature",
                            "result_value": "25",
                            "test_type": "numeric",
                            "value_type": "optimal",
                            "measurement_unit": "°C",
                            "confidence_level": "high",
                            "tested_date": "2023-01-03",
                            "notes": "Optimal growth temperature"
                        },
                        {
                            "test_code": "catalase",
                            "result_value": "+",
                            "test_type": "boolean",
                            "value_type": None,
                            "measurement_unit": None,
                            "confidence_level": "high",
                            "tested_date": "2023-01-04",
                            "notes": "Positive catalase test"
                        }
                    ]
                },
                {
                    "strain_identifier": "LYS-TEMPLATE-002",
                    "scientific_name": "Lysobacter antibioticus",
                    "common_name": "Template strain 2",
                    "description": "Second example strain",
                    "isolation_source": "Agricultural soil",
                    "isolation_location": "Field example",
                    "isolation_date": "2023-02-01",
                    "notes": "Second template strain",
                    "test_results": [
                        {
                            "test_code": "oxidase",
                            "result_value": "+/-",
                            "test_type": "boolean",
                            "value_type": None,
                            "measurement_unit": None,
                            "confidence_level": "medium",
                            "tested_date": "2023-02-02",
                            "notes": "Weak positive reaction"
                        },
                        {
                            "test_code": "ph_level",
                            "result_value": "7.0",
                            "test_type": "numeric",
                            "value_type": "optimal",
                            "measurement_unit": "pH",
                            "confidence_level": "high",
                            "tested_date": "2023-02-03",
                            "notes": "Neutral pH optimal"
                        }
                    ]
                }
            ]
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            
            print(f"✓ JSON template created: {output_file}")
            print(f"✓ Template contains {len(template['strains'])} example strains")
            print(f"✓ Edit this file with your data and use --import to load it")
            
        except Exception as e:
            print(f"✗ Error creating template: {e}")


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description='Import Lysobacter data from JSON files')
    parser.add_argument('--json-file', help='Path to JSON file to import')
    parser.add_argument('--import', action='store_true', dest='do_import', help='Import data from JSON file')
    parser.add_argument('--generate-template', help='Generate JSON template file')
    parser.add_argument('--validate-only', action='store_true', help='Only validate JSON structure without importing')
    parser.add_argument('--db-host', default='localhost', help='Database host')
    parser.add_argument('--db-port', default='5433', help='Database port')
    parser.add_argument('--db-name', default='lysobacter_db', help='Database name')
    parser.add_argument('--db-user', default='lysobacter_user', help='Database user')
    parser.add_argument('--db-password', default='lysobacter_password', help='Database password')
    
    args = parser.parse_args()
    
    # Generate template
    if args.generate_template:
        # Don't need database connection for template generation
        importer = LysobacterJSONImporter({})
        importer.generate_json_template(args.generate_template)
        return
    
    # Validate or import
    if not args.json_file:
        print("✗ Please specify --json-file")
        sys.exit(1)
    
    if not os.path.exists(args.json_file):
        print(f"✗ JSON file not found: {args.json_file}")
        sys.exit(1)
    
    # Database configuration
    db_config = {
        'host': args.db_host,
        'port': args.db_port,
        'database': args.db_name,
        'user': args.db_user,
        'password': args.db_password
    }
    
    # Initialize importer
    importer = LysobacterJSONImporter(db_config)
    
    try:
        # For validation only, we still need to connect to load test cache
        if args.validate_only:
            print("Validating JSON structure...")
            with open(args.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if importer.validate_json_structure(data):
                print("✓ JSON validation passed")
            else:
                print("✗ JSON validation failed")
                sys.exit(1)
            return
        
        # Full import
        if args.do_import:
            importer.connect()
            importer.load_test_cache()
            
            result = importer.import_from_json(args.json_file)
            
            if result['strains'] > 0:
                print(f"✓ Successfully imported {result['strains']} strains and {result['test_results']} test results")
            else:
                print("✗ No data was imported")
                sys.exit(1)
        else:
            print("✗ Please specify --import to import data or --validate-only to validate")
            
    except Exception as e:
        print(f"✗ Operation failed: {e}")
        sys.exit(1)
    finally:
        importer.disconnect()


if __name__ == '__main__':
    main() 