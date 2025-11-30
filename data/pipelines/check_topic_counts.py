import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in environment.")
    exit(1)

supabase = create_client(url, key)

def check_counts():
    try:
        response = supabase.table("mvp2_topics").select("country_code, article_count").eq("country_code", "KR").execute()
        data = response.data
        
        print(f"\nChecking 'KR' topics specifically:")
        print(f"Count: {len(data)}")
        for item in data:
            cc = item.get("country_code")
            ac = item.get("article_count")
            print(f"Value: '{cc}', Count: {ac}")
            
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    check_counts()
