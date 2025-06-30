#!/usr/bin/env python3
"""
Apply salt tolerance test type fix to the database
"""

import subprocess
import os
import sys

def run_sql_migration():
    """Apply the SQL migration to fix salt tolerance test type"""
    
    # Path to the SQL migration file
    migration_file = "backend/database/migrations/fix_salt_tolerance_test_type.sql"
    
    if not os.path.exists(migration_file):
        print(f"Migration file not found: {migration_file}")
        return False
    
    # Check if we're in Docker environment or local
    try:
        # Try Docker approach first (for production)
        cmd = [
            "docker", "exec", "-i", "lysodata_db",
            "psql", "-U", "lyso_user", "-d", "lyso_db"
        ]
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("Applying migration via Docker...")
        result = subprocess.run(
            cmd,
            input=sql_content,
            text=True,
            capture_output=True
        )
        
        if result.returncode == 0:
            print("✅ Migration applied successfully!")
            print("Output:", result.stdout)
            return True
        else:
            print("❌ Migration failed via Docker:")
            print("Error:", result.stderr)
            
            # Try local psql as fallback
            print("\nTrying local psql connection...")
            cmd_local = [
                "psql", 
                "-h", "localhost", 
                "-p", "5432",
                "-U", "lyso_user", 
                "-d", "lyso_db",
                "-f", migration_file
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = 'lyso_pass'
            
            result_local = subprocess.run(cmd_local, env=env, capture_output=True, text=True)
            
            if result_local.returncode == 0:
                print("✅ Migration applied successfully via local psql!")
                print("Output:", result_local.stdout)
                return True
            else:
                print("❌ Migration failed via local psql:")
                print("Error:", result_local.stderr)
                return False
                
    except FileNotFoundError:
        print("Docker not found, trying local psql...")
        # Direct local approach
        cmd_local = [
            "psql", 
            "-h", "localhost", 
            "-p", "5432",
            "-U", "lyso_user", 
            "-d", "lyso_db",
            "-f", migration_file
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = 'lyso_pass'
        
        result = subprocess.run(cmd_local, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migration applied successfully!")
            print("Output:", result.stdout)
            return True
        else:
            print("❌ Migration failed:")
            print("Error:", result.stderr)
            return False

if __name__ == "__main__":
    print("🔧 Fixing Salt Tolerance test type from boolean to numeric...")
    
    success = run_sql_migration()
    
    if success:
        print("\n✅ Migration completed! Salt tolerance test is now numeric.")
        print("🔄 Please restart the backend server to see changes.")
        sys.exit(0)
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1) 