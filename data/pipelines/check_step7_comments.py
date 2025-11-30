import os
import sys
from supabase import create_client
from dotenv import load_dotenv

# Load env
load_dotenv(".env.local")

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not url or not key:
    print("Error: Missing Supabase credentials in .env.local")
    sys.exit(1)

supabase = create_client(url, key)

def check_comments():
    print("--- Verifying Step 7: Editor Comments ---")
    
    # Check Global Topics
    print("\nChecking 'mvp2_global_topics'...")
    res = supabase.from_("mvp2_global_topics").select("id, title_ko, editor_comment", count="exact").not_.is_("editor_comment", "null").execute()
    count = res.count
    print(f"   -> Found {count} global topics with Editor Comment.")
    
    if count > 0:
        sample = res.data[0]
        print(f"   -> Sample (ID: {sample['id']}):\n{sample['editor_comment'][:200]}...")
        print("\n✅ Step 7 Verification SUCCESS")
    else:
        print("\n⚠️ Step 7 Verification INCOMPLETE (No comments found)")

if __name__ == "__main__":
    check_comments()
