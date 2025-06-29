#!/usr/bin/env python3
"""
Import strain data from JSON file to LysoData-Miner database
"""

import os
import sys
import json
import psycopg2
from psycopg2 import sql
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def get_db_config():
    """Получение конфигурации БД из переменных окружения"""
    return {
        'host': os.getenv('DB_HOST', 'database'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('POSTGRES_DB', 'lysobacter_db'),
        'user': os.getenv('POSTGRES_USER', 'lysobacter_user'),
        'password': os.getenv('POSTGRES_PASSWORD', 'SecureLysoPassword2025!')
    }

def load_json_data(file_path):
    """Загрузка данных из JSON файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"❌ Error loading JSON file: {e}")
        return None

def insert_strain(cursor, strain_data):
    """Вставка данных штамма в базу"""
    try:
        # Вставка штамма
        cursor.execute("""
            INSERT INTO lysobacter.strains 
            (strain_identifier, scientific_name, common_name, description, 
             isolation_source, isolation_location, isolation_date, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING strain_id
        """, (
            strain_data.get('strain_identifier'),
            strain_data.get('scientific_name'),
            strain_data.get('common_name'),
            strain_data.get('description'),
            strain_data.get('isolation_source'),
            strain_data.get('isolation_location'),
            strain_data.get('isolation_date'),
            strain_data.get('notes')
        ))
        
        strain_id = cursor.fetchone()[0]
        logger.info(f"   ✅ Strain inserted: {strain_data.get('strain_identifier')} (ID: {strain_id})")
        
        # Вставка результатов тестов
        test_results = strain_data.get('test_results', [])
        for test_result in test_results:
            insert_test_result(cursor, strain_id, test_result)
        
        return strain_id
        
    except Exception as e:
        logger.error(f"   ❌ Error inserting strain {strain_data.get('strain_identifier')}: {e}")
        return None

def get_test_id(cursor, test_code):
    """Получение ID теста по коду"""
    cursor.execute("""
        SELECT test_id FROM lysobacter.tests 
        WHERE test_code = %s
    """, (test_code,))
    
    result = cursor.fetchone()
    return result[0] if result else None

def insert_test_result(cursor, strain_id, test_result):
    """Вставка результата теста"""
    try:
        test_code = test_result.get('test_code')
        test_id = get_test_id(cursor, test_code)
        
        if not test_id:
            logger.warning(f"     ⚠️  Test not found: {test_code}")
            return
        
        result_value = test_result.get('result')
        
        # Определяем тип результата и вставляем в соответствующую таблицу
        if isinstance(result_value, bool) or result_value in ['positive', 'negative', '+', '-', 'yes', 'no']:
            # Boolean результат
            bool_value = result_value in [True, 'positive', '+', 'yes']
            cursor.execute("""
                INSERT INTO lysobacter.test_results_boolean 
                (strain_id, test_id, result_value)
                VALUES (%s, %s, %s)
            """, (strain_id, test_id, bool_value))
            
        elif isinstance(result_value, (int, float)) or (isinstance(result_value, str) and result_value.replace('.', '').isdigit()):
            # Numeric результат
            cursor.execute("""
                INSERT INTO lysobacter.test_results_numeric 
                (strain_id, test_id, result_value)
                VALUES (%s, %s, %s)
            """, (strain_id, test_id, float(result_value)))
            
        else:
            # Text результат
            cursor.execute("""
                INSERT INTO lysobacter.test_results_text 
                (strain_id, test_id, result_value)
                VALUES (%s, %s, %s)
            """, (strain_id, test_id, str(result_value)))
            
        logger.info(f"     ✅ Test result: {test_code} = {result_value}")
        
    except Exception as e:
        logger.error(f"     ❌ Error inserting test result {test_code}: {e}")

def import_strain_data(config, json_file_path):
    """Импорт данных штаммов"""
    logger.info(f"📄 Loading data from {json_file_path}...")
    
    data = load_json_data(json_file_path)
    if not data:
        return False
    
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        strains = data.get('strains', [])
        logger.info(f"🧬 Importing {len(strains)} strains...")
        
        imported_count = 0
        for strain in strains:
            strain_id = insert_strain(cursor, strain)
            if strain_id:
                imported_count += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Successfully imported {imported_count} strains")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database error: {e}")
        return False

def main():
    """Главная функция"""
    logger.info("🧬 LysoData-Miner Strain Data Import")
    logger.info("=" * 50)
    
    # Получение конфигурации
    config = get_db_config()
    
    # Путь к JSON файлу
    json_file = '/app/database/data/import_20250628.json'
    
    if not os.path.exists(json_file):
        logger.error(f"❌ JSON file not found: {json_file}")
        sys.exit(1)
    
    # Импорт данных
    if import_strain_data(config, json_file):
        logger.info("🎉 Data import completed successfully!")
        
        # Показать статистику
        try:
            conn = psycopg2.connect(**config)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM lysobacter.strains")
            strain_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM lysobacter.test_results_boolean")
            bool_results = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM lysobacter.test_results_numeric") 
            num_results = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM lysobacter.test_results_text")
            text_results = cursor.fetchone()[0]
            
            logger.info("📊 Database Statistics:")
            logger.info(f"   Strains: {strain_count}")
            logger.info(f"   Boolean results: {bool_results}")
            logger.info(f"   Numeric results: {num_results}")
            logger.info(f"   Text results: {text_results}")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
        
        sys.exit(0)
    else:
        logger.error("❌ Data import failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 