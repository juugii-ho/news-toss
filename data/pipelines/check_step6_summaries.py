import os
import sys
from supabase import create_client
from dotenv import load_dotenv

# Load env
load_dotenv(".env.local")

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: Missing Supabase credentials in .env.local")
    sys.exit(1)

supabase = create_client(url, key)

def check_summaries():
    print("--- Verifying Step 6: AI Summaries ---")
    
    # 1. Check Local Topics
    print("\n1. Checking 'mvp2_topics' (Local)...")
    res_local = supabase.from_("mvp2_topics").select("id, ai_summary", count="exact").not_.is_("ai_summary", "null").execute()
    count_local = res_local.count
    print(f"   -> Found {count_local} local topics with AI summary.")
    
    if count_local > 0:
        sample = res_local.data[0]
        print(f"   -> Sample (ID: {sample['id']}): {sample['ai_summary'][:50]}...")
    else:
        print("   -> WARNING: No local summaries found.")

    # 2. Check Global Topics
    print("\n2. Checking 'mvp2_global_topics' (Global)...")
    res_global = supabase.from_("mvp2_global_topics").select("id, title_ko, ai_summary", count="exact").not_.is_("ai_summary", "null").execute()
    count_global = res_global.count
    print(f"   -> Found {count_global} global topics with AI summary.")
    
    if count_global > 0:
        sample = res_global.data[0]
        print(f"   -> Sample (ID: {sample['id']}): {sample['ai_summary'][:50]}...")
    else:
        print("   -> WARNING: No global summaries found.")

    if count_local > 0 and count_global > 0:
        print("\n✅ Step 6 Verification SUCCESS")
    else:
        print("\n⚠️ Step 6 Verification INCOMPLETE")

if __name__ == "__main__":
    check_summaries()
