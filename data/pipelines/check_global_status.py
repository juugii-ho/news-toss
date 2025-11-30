import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv("backend/.env")
load_dotenv(".env.local")
load_dotenv(".env")

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not url or not key:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase: Client = create_client(url, key)

def check_global_status():
    print("Checking Global Topics (mvp2_megatopics)...")
    
    # Total count
    res_total = supabase.table("mvp2_megatopics").select("id", count="exact").execute()
    print(f"Total Global Topics: {res_total.count}")

    # Published count
    res_pub = supabase.table("mvp2_megatopics").select("id", count="exact").eq("is_published", True).execute()
    print(f"Published Global Topics: {res_pub.count}")
    
    # Check if any have batch_id
    res_batch = supabase.table("mvp2_megatopics").select("batch_id").not_.is_("batch_id", "null").limit(5).execute()
    print(f"Sample Batch IDs: {[r['batch_id'] for r in res_batch.data]}")

if __name__ == "__main__":
    check_global_status()
