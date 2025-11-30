import os
from dotenv import load_dotenv
from supabase import create_client

# Load env from backend
load_dotenv('backend/.env')

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not url or not key:
    print("❌ No credentials")
    exit()

supabase = create_client(url, key)

print("Fetching 1 row from mvp2_megatopics...")
try:
    response = supabase.table("mvp2_megatopics").select("*").limit(1).execute()
    if response.data:
        print("✅ Row keys:", response.data[0].keys())
        print("Sample row:", response.data[0])
    else:
        print("⚠️ No data found")
except Exception as e:
    print(f"❌ Error: {e}")
