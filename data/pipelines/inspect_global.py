import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

def inspect_columns():
    try:
        print("Inspecting mvp2_megatopics...")
        res = supabase.table("mvp2_megatopics").select("*").limit(1).execute()
        if res.data:
            print("Columns:", res.data[0].keys())
        else:
            print("No data in mvp2_global_topics")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_columns()
