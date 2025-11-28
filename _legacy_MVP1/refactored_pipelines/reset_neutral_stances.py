import os
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

def reset_neutral_stances():
    print("Checking for articles with stance_score = 50...")
    
    # Count them first
    res = supabase.table("mvp_articles").select("id", count="exact").eq("stance_score", 50).execute()
    count = res.count
    print(f"Found {count} articles with score 50.")
    
    if count == 0:
        print("No articles to reset.")
        return

    print("Resetting stance and stance_score to NULL...")
    
    # Update in batches (Supabase limit)
    # Actually, we can just update all where eq 50. 
    # But for safety and timeouts, maybe loop? 
    # Let's try a direct update first.
    
    try:
        # Supabase-py update doesn't support bulk update without ID usually, 
        # but .eq() should work for 'update where'.
        # However, the library might require specific IDs for safety.
        # Let's fetch IDs and update in chunks.
        
        offset = 0
        batch_size = 100
        
        while True:
            res = supabase.table("mvp_articles").select("id").eq("stance_score", 50).limit(batch_size).execute()
            articles = res.data
            
            if not articles:
                break
                
            ids = [a['id'] for a in articles]
            print(f"Resetting batch of {len(ids)} articles...")
            
            supabase.table("mvp_articles").update({"stance": None, "stance_score": None}).in_("id", ids).execute()
            
    except Exception as e:
        print(f"Error: {e}")
        
    print("Done.")

if __name__ == "__main__":
    reset_neutral_stances()
