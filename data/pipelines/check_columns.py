import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('backend/.env')

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_columns():
    # Fetch one row to see keys
    response = supabase.table("mvp2_topics").select("*").limit(1).execute()
    if response.data:
        print("Columns in mvp2_topics:")
        print(response.data[0].keys())
    else:
        print("No data in mvp2_topics to infer columns.")

if __name__ == "__main__":
    check_columns()
