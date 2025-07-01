"""
Django-style migration for removing spore_formation test
File: 0002_remove_spore_formation.py
Date: 2025-07-01
Author: LysoData-Miner System

Removes spore_formation test as all Lysobacter are non-spore-forming gram-negative rods.
This migration will be applied automatically during deployment.
"""

def apply_migration():
    """Apply the migration to remove spore_formation test"""
    
    import psycopg2
    import os
    
    # Database connection from environment
    db_config = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': os.getenv('POSTGRES_PORT', '5432'),
        'database': os.getenv('POSTGRES_DB', 'lysobacter_db'),
        'user': os.getenv('POSTGRES_USER', 'lysobacter_user'),
        'password': os.getenv('POSTGRES_PASSWORD', 'lysobacter_password')
    }
    
    try:
        # Connect to database
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Check if spore_formation test exists
        cursor.execute("""
            SELECT test_id FROM lysobacter.tests 
            WHERE test_code = 'spore_formation'
        """)
        
        spore_test = cursor.fetchone()
        
        if spore_test:
            spore_test_id = spore_test[0]
            print(f"Found spore_formation test with ID: {spore_test_id}")
            
            # Remove test results from all results tables
            cursor.execute("""
                DELETE FROM lysobacter.test_results_boolean 
                WHERE test_id = %s
            """, (spore_test_id,))
            boolean_deleted = cursor.rowcount
            
            cursor.execute("""
                DELETE FROM lysobacter.test_results_numeric 
                WHERE test_id = %s
            """, (spore_test_id,))
            numeric_deleted = cursor.rowcount
            
            cursor.execute("""
                DELETE FROM lysobacter.test_results_text 
                WHERE test_id = %s
            """, (spore_test_id,))
            text_deleted = cursor.rowcount
            
            # Remove the test itself
            cursor.execute("""
                DELETE FROM lysobacter.tests 
                WHERE test_id = %s
            """, (spore_test_id,))
            
            # Commit changes
            conn.commit()
            
            print(f"✓ Migration 0002_remove_spore_formation applied successfully")
            print(f"✓ Removed spore_formation test (ID: {spore_test_id})")
            print(f"✓ Deleted {boolean_deleted} boolean results")
            print(f"✓ Deleted {numeric_deleted} numeric results") 
            print(f"✓ Deleted {text_deleted} text results")
            
        else:
            print("✓ Migration 0002_remove_spore_formation: spore_formation test not found, already applied")
            
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        print(f"✗ Migration 0002_remove_spore_formation failed: {e}")
        raise
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


def rollback_migration():
    """Rollback migration (not recommended - adds back removed test)"""
    print("WARNING: Rollback not recommended for this migration")
    print("spore_formation test was removed because all Lysobacter are non-spore-forming")
    

if __name__ == "__main__":
    apply_migration() 