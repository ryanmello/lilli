"""
Run database migrations against Supabase PostgreSQL.

Usage:
    python scripts/run_migrations.py

Requires DATABASE_URL in .env file. Get it from:
    Supabase Dashboard > Project Settings > Database > Connection string (URI)
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import psycopg2
from dotenv import load_dotenv
from utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

MIGRATIONS_DIR = Path(__file__).parent.parent / "supabase" / "migrations"

def get_database_url() -> str:
    """Get database URL from environment."""
    db_url = os.getenv("SUPABASE_DATABASE_URL")
    if not db_url:
        print("\n❌ DATABASE_URL not found in .env file.")
        print("\nTo get your connection string:")
        print("  1. Go to https://supabase.com/dashboard")
        print("  2. Select your project")
        print("  3. Go to Project Settings > Database")
        print("  4. Copy the 'Connection string' (URI format)")
        print("  5. Add to your .env file as DATABASE_URL=<connection_string>")
        print("\nExample:")
        print("  DATABASE_URL=postgresql://postgres.xxxxx:password@aws-0-us-east-1.pooler.supabase.com:6543/postgres")
        sys.exit(1)
    return db_url


def run_migrations():
    """Run all SQL migration files in order."""
    db_url = get_database_url()
    
    # Get all migration files sorted by name
    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    
    if not migration_files:
        print("No migration files found in", MIGRATIONS_DIR)
        return
    
    print(f"\n📦 Found {len(migration_files)} migration(s) to run:\n")
    for f in migration_files:
        print(f"  - {f.name}")
    
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("\n🚀 Running migrations...\n")
        
        for migration_file in migration_files:
            print(f"  ▶ Running {migration_file.name}...")
            
            sql = migration_file.read_text(encoding="utf-8")
            cursor.execute(sql)
            
            print(f"  ✅ {migration_file.name} completed")
        
        cursor.close()
        conn.close()
        
        print("\n✨ All migrations completed successfully!\n")
        
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_migrations()
