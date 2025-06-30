#!/usr/bin/env python3
import os
import json
import psycopg2

def main():
    print("🧬 Test Import Script")
    print("=" * 30)
    
    # Проверка файла
    json_file = '/app/database/data/import_20250628.json'
    print(f"1. Checking JSON file: {json_file}")
    if os.path.exists(json_file):
        print("   ✅ File exists")
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                print(f"   ✅ JSON loaded, {len(data.get('strains', []))} strains found")
        except Exception as e:
            print(f"   ❌ JSON error: {e}")
            return
    else:
        print("   ❌ File not found")
        return
    
    # Проверка подключения к БД
    print("2. Testing database connection...")
    try:
        config = {
            'host': os.getenv('DB_HOST', 'database'),
            'port': os.getenv('DB_PORT', '5432'), 
            'database': os.getenv('POSTGRES_DB', 'lysobacter_db'),
            'user': os.getenv('POSTGRES_USER', 'lysobacter_user'),
            'password': os.getenv('POSTGRES_PASSWORD', 'SecureLysoPassword2025!')
        }
        print(f"   Config: {config['host']}:{config['port']}/{config['database']}")
        
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM lysobacter.strains")
        strain_count = cursor.fetchone()[0]
        print(f"   ✅ DB connected, current strains: {strain_count}")
        
        # Проверим первый штамм из JSON
        strains = data.get('strains', [])
        if strains:
            first_strain = strains[0]
            identifier = first_strain.get('strain_identifier')
            print(f"3. Testing strain insertion: {identifier}")
            
            try:
                cursor.execute("""
                    INSERT INTO lysobacter.strains 
                    (strain_identifier, scientific_name, common_name, description, 
                     isolation_source, isolation_location, isolation_date, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING strain_id
                """, (
                    first_strain.get('strain_identifier'),
                    first_strain.get('scientific_name'),
                    first_strain.get('common_name'),
                    first_strain.get('description'),
                    first_strain.get('isolation_source'),
                    first_strain.get('isolation_location'),
                    first_strain.get('isolation_date'),
                    first_strain.get('notes')
                ))
                
                strain_id = cursor.fetchone()[0]
                print(f"   ✅ Strain inserted successfully: ID {strain_id}")
                
                conn.commit()
                
            except Exception as e:
                print(f"   ❌ Insert error: {e}")
                conn.rollback()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"   ❌ DB error: {e}")
    
    print("Test completed!")

if __name__ == "__main__":
    main() 