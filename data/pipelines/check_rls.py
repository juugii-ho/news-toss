import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
key = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not url or not key:
    print("Error: NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY not found in environment.")
    # Try loading from .env.local if not in .env
    # But python-dotenv loads .env by default.
    # Let's assume user has them in .env or .env.local
    # If not found, we might need to read .env.local manually
    pass

if not key:
    print("Trying to read .env.local...")
    try:
        with open(".env.local", "r") as f:
            for line in f:
                if line.startswith("NEXT_PUBLIC_SUPABASE_ANON_KEY="):
                    key = line.strip().split("=", 1)[1].strip('"').strip("'")
                if line.startswith("NEXT_PUBLIC_SUPABASE_URL="):
                    url = line.strip().split("=", 1)[1].strip('"').strip("'")
    except Exception as e:
        print(f"Error reading .env.local: {e}")

if not url or not key:
    print("Failed to load credentials.")
    exit(1)

print(f"Using URL: {url}")
print(f"Using Anon Key: {key[:10]}...")

supabase = create_client(url, key)

def check_rls():
    try:
        print("Attempting to fetch 'KR' topics with Anon Key...")
        response = supabase.table("mvp2_topics").select("country_code").eq("country_code", "KR").execute()
        data = response.data
        
        print(f"Count: {len(data)}")
        if len(data) == 0:
            print("RLS likely blocking access or no data.")
        else:
            print("Access successful.")
            
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    check_rls()
