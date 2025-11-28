import os
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path

# Load environment
root_dir = Path(__file__).resolve().parent
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def reset_today_history():
    today_str = datetime.now().strftime('%Y-%m-%d')
    print(f"Deleting history records for date: {today_str}...")
    
    # Delete all records for today
    res = supabase.table("mvp_topic_history").delete().eq("date", today_str).execute()
    
    print(f"Deleted records. (Count not returned by delete usually, but check data attribute)")
    print(f"Data: {len(res.data) if res.data else 0} records deleted.")

if __name__ == "__main__":
    reset_today_history()
