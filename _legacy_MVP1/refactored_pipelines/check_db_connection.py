import os
import psycopg2
from dotenv import load_dotenv

# Try loading from .env first, then .env.local
load_dotenv('.env')
load_dotenv('.env.local')

DATABASE_URL = os.getenv("DATABASE_URL")

def check_connection():
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment variables.")
        return False

    print(f"Attempting to connect to: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else '...'}...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        print(f"✅ Connected successfully!")
        print(f"Database Version: {db_version[0]}")
        
        # Check if mvp_topics table exists
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'mvp_topics');")
        table_exists = cur.fetchone()[0]
        if table_exists:
            print("✅ Table 'mvp_topics' found.")
        else:
            print("⚠️ Table 'mvp_topics' NOT found.")
            
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    check_connection()
