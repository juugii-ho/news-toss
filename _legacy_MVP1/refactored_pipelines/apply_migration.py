import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

# Load env
root_dir = Path(__file__).resolve().parents[2]
load_dotenv(root_dir / ".env.local")
if not os.getenv("DATABASE_URL"):
    load_dotenv(root_dir / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Loaded DATABASE_URL: {DATABASE_URL[:20]}..." if DATABASE_URL else "DATABASE_URL is None")

def apply_migration():
    if not DATABASE_URL:
        print("DATABASE_URL not found.")
        return

    migration_file = root_dir / "infra/supabase/migrations/20251126000001_add_divergence_score.sql"
    
    try:
        with open(migration_file, "r") as f:
            sql = f.read()
            
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print(f"Applying migration: {migration_file.name}")
        cur.execute(sql)
        conn.commit()
        
        print("Migration applied successfully.")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error applying migration: {e}")

if __name__ == "__main__":
    apply_migration()
