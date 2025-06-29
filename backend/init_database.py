#!/usr/bin/env python3
"""
Database initialization script for LysoData-Miner
Initializes PostgreSQL database with schema and sample data
"""

import os
import sys
import time
import subprocess
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

def wait_for_database(config, max_attempts=30):
    """Ожидание готовности базы данных"""
    logger.info("🔄 Waiting for database...")
    
    for attempt in range(max_attempts):
        try:
            conn = psycopg2.connect(**config)
            conn.close()
            logger.info("✅ Database is ready!")
            return True
        except psycopg2.OperationalError:
            if attempt < max_attempts - 1:
                time.sleep(2)
                logger.info(f"   Attempt {attempt + 1}/{max_attempts}...")
            else:
                logger.error("❌ Database connection timeout")
                return False
    return False

def check_if_initialized(config):
    """Проверка, инициализирована ли база данных"""
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Проверяем наличие таблиц
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name IN ('test_categories', 'tests', 'strains')
        """)
        table_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return table_count >= 3
        
    except Exception as e:
        logger.error(f"Error checking initialization: {e}")
        return False

def run_sql_file(config, sql_file_path):
    """Выполнение SQL файла"""
    if not os.path.exists(sql_file_path):
        logger.warning(f"⚠️  SQL file not found: {sql_file_path}")
        return False
        
    logger.info(f"📄 Executing {os.path.basename(sql_file_path)}...")
    
    try:
        # Используем psql для выполнения файла
        env = os.environ.copy()
        env['PGPASSWORD'] = config['password']
        
        cmd = [
            'psql',
            '-h', config['host'],
            '-p', str(config['port']),
            '-U', config['user'],
            '-d', config['database'],
            '-f', sql_file_path,
            '-v', 'ON_ERROR_STOP=1'
        ]
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"✅ {os.path.basename(sql_file_path)} executed successfully")
            return True
        else:
            logger.error(f"❌ Error executing {sql_file_path}: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Exception executing {sql_file_path}: {e}")
        return False

def initialize_database(config):
    """Инициализация базы данных"""
    logger.info("🚀 Initializing database...")
    
    # Список SQL файлов для выполнения (в порядке)
    sql_files = [
        '/app/database/schema/01_create_tables.sql',
        '/app/database/schema/02_insert_reference_data.sql',
        '/app/database/schema/03_views_and_functions.sql'
    ]
    
    for sql_file in sql_files:
        if not run_sql_file(config, sql_file):
            logger.error(f"❌ Failed to execute {sql_file}")
            return False
    
    return True

def show_statistics(config):
    """Показать статистику базы данных"""
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Статистика по таблицам
        stats_queries = [
            ("Test Categories", "SELECT COUNT(*) FROM test_categories"),
            ("Tests", "SELECT COUNT(*) FROM tests"),
            ("Strains", "SELECT COUNT(*) FROM strains"),
            ("Test Results", "SELECT COUNT(*) FROM test_results"),
            ("Collection Numbers", "SELECT COUNT(*) FROM collection_numbers")
        ]
        
        logger.info("📊 Database Statistics:")
        for name, query in stats_queries:
            try:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                logger.info(f"   {name}: {count}")
            except Exception:
                logger.info(f"   {name}: n/a")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")

def main():
    """Главная функция"""
    logger.info("🔄 LysoData-Miner Database Initialization")
    logger.info("=" * 50)
    
    # Получение конфигурации
    config = get_db_config()
    
    # Ожидание базы данных
    if not wait_for_database(config):
        sys.exit(1)
    
    # Проверка инициализации
    logger.info("📊 Checking if data initialization is needed...")
    if check_if_initialized(config):
        logger.info("✅ Database already initialized")
        show_statistics(config)
        logger.info("🎉 Database initialization complete!")
        sys.exit(0)
    
    # Инициализация
    if initialize_database(config):
        logger.info("✅ Database initialized successfully")
        show_statistics(config)
        logger.info("🎉 Database initialization complete!")
        sys.exit(0)
    else:
        logger.error("❌ Database initialization failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 