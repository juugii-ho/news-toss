from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')
supabase = create_client(os.getenv('NEXT_PUBLIC_SUPABASE_URL'), os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY'))

rows = supabase.table('mvp2_megatopics').select('id, countries').is_('country_count', 'null').execute().data
print(f'Found {len(rows)} rows to update')

for row in rows:
    if row['countries']:
        count = len(row['countries'])
        supabase.table('mvp2_megatopics').update({'country_count': count}).eq('id', row['id']).execute()
        print(f"Updated {row['id']} with count {count}")
