#!/usr/bin/env python3
import os
import json
import psycopg2

def main():
    print("🧬 Simple Import Script")
    
    # Конфигурация БД
    config = {
        'host': 'database',
        'port': '5432',
        'database': 'lysobacter_db',
        'user': 'lysobacter_user',
        'password': 'SecureLysoPassword2025!'
    }
    
    # Загрузка данных
    with open('/app/database/data/import_20250628.json', 'r') as f:
        data = json.load(f)
    
    strains = data.get('strains', [])
    print(f"Found {len(strains)} strains to import")
    
    # Подключение к БД
    conn = psycopg2.connect(**config)
    cursor = conn.cursor()
    
    # Импорт каждого штамма
    for strain in strains:
        identifier = strain.get('strain_identifier')
        
        # Проверим, существует ли уже
        cursor.execute("SELECT strain_id FROM lysobacter.strains WHERE strain_identifier = %s", (identifier,))
        if cursor.fetchone():
            print(f"   ⚠️  Strain {identifier} already exists, skipping")
            continue
        
        print(f"   📦 Importing {identifier}...")
        
        cursor.execute("""
            INSERT INTO lysobacter.strains 
            (strain_identifier, scientific_name, common_name, description, 
             isolation_source, isolation_location, isolation_date, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING strain_id
        """, (
            strain.get('strain_identifier'),
            strain.get('scientific_name'),
            strain.get('common_name'),
            strain.get('description'),
            strain.get('isolation_source'),
            strain.get('isolation_location'),
            strain.get('isolation_date'),
            strain.get('notes')
        ))
        
        strain_id = cursor.fetchone()[0]
        print(f"   ✅ Strain {identifier} imported with ID {strain_id}")
    
    conn.commit()
    
    # Статистика
    cursor.execute("SELECT COUNT(*) FROM lysobacter.strains")
    total_strains = cursor.fetchone()[0]
    print(f"✅ Import completed! Total strains in database: {total_strains}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main() 