import os
from dotenv import load_dotenv
from supabase import create_client

# Load env
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
load_dotenv(os.path.join(project_root, 'backend', '.env'))

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase = create_client(url, key)

print("Checking Megatopics Headlines...")
response = supabase.table("mvp2_megatopics").select("name, headline").order("created_at", desc=True).limit(20).execute()
for row in response.data:
    print(f"[{'✅' if row['headline'] else '❌'}] {row['name'][:30]}... -> {row['headline']}")

print("\nChecking Local Topics Headlines...")
response = supabase.table("mvp2_topics").select("topic_name, headline").eq("country_code", "KR").order("created_at", desc=True).limit(20).execute()
for row in response.data:
    print(f"[{'✅' if row['headline'] else '❌'}] {row['topic_name'][:30]}... -> {row['headline']}")
