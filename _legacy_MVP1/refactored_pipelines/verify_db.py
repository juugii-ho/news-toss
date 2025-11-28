import os
from dotenv import load_dotenv
from supabase import create_client
from pathlib import Path

# Load env vars
root_dir = Path('.').resolve()
load_dotenv(root_dir / '.env.local')
load_dotenv(root_dir / '.env')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Missing environment variables")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=== Verifying Headlines in DB ===")

# 1. Check total count
try:
    result = supabase.table('mvp_topics').select('count', count='exact').not_.is_('headline', 'null').execute()
    print(f"Total topics with headline: {result.count}")
except Exception as e:
    print(f"Error checking count: {e}")

# 2. Global Megatopics (Latest by ID)
print("\n=== Global Megatopics (Latest by ID) ===")
try:
    megas = supabase.table('mvp_topics').select('title_kr,headline,country_count,date,id').gt('country_count', 1).not_.is_('headline', 'null').order('id', desc=True).limit(5).execute()
    for topic in megas.data:
        print(f"[ID: {topic.get('id')}] [Countries: {topic.get('country_count')}] {topic.get('title_kr')}")
        print(f"   -> {topic.get('headline')}")
except Exception as e:
    print(f"Error checking megatopics: {e}")

# 3. National Topics (Latest by ID)
print("\n=== National Topics (Latest by ID) ===")
try:
    nationals = supabase.table('mvp_topics').select('title_kr,headline,country_count,date,id').eq('country_count', 1).not_.is_('headline', 'null').order('id', desc=True).limit(5).execute()
    for topic in nationals.data:
        print(f"[ID: {topic.get('id')}] [National] {topic.get('title_kr')}")
        print(f"   -> {topic.get('headline')}")
except Exception as e:
    print(f"Error checking national topics: {e}")
