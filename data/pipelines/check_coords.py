import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load env
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, "..", "..", "backend", ".env")
load_dotenv(env_path)

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

def main():
    print("🚀 Checking Coordinates...")
    
    # Fetch Megatopics
    response = supabase.table("mvp2_megatopics").select("name, x, y").execute()
    megatopics = response.data
    
    print(f"\n--- Megatopics ({len(megatopics)}) ---")
    for m in megatopics:
        print(f"[{m['name']}] -> ({m['x']}, {m['y']})")
        
    # Fetch Local Topics (Sample)
    response = supabase.table("mvp2_topics").select("topic_name, x, y").limit(10).execute()
    topics = response.data
    
    print(f"\n--- Local Topics (Sample 10) ---")
    for t in topics:
        print(f"[{t['topic_name']}] -> ({t['x']}, {t['y']})")

if __name__ == "__main__":
    main()
