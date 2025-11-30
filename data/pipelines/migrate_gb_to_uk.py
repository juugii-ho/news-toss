#!/usr/bin/env python3
"""
Migrate GB country code to UK in all tables
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or key:
    print("Error: Service role key required for updates.")
    exit(1)

supabase = create_client(url, key)

def migrate_gb_to_uk():
    print("🔄 Starting GB → UK migration...")
    
    tables_to_update = [
        "mvp2_news_sources",
        "mvp2_articles", 
        "mvp2_topics",
        "mvp2_megatopics"
    ]
    
    total_updated = 0
    
    for table in tables_to_update:
        try:
            print(f"\n📊 Updating {table}...")
            
            # Update country_code from GB to UK
            result = supabase.table(table).update({"country_code": "UK"}).eq("country_code", "GB").execute()
            
            # Count updated rows (if available in response)
            count = len(result.data) if result.data else 0
            print(f"  ✅ Updated {count} rows in {table}")
            total_updated += count
            
        except Exception as e:
            print(f"  ⚠️  Error updating {table}: {e}")
    
    # Also update countries array in megatopics
    try:
        print(f"\n📊 Updating countries array in mvp2_megatopics...")
        
        # Fetch all megatopics with GB in countries array
        res = supabase.table("mvp2_megatopics").select("id, countries").execute()
        
        updated_count = 0
        for topic in res.data:
            if topic.get('countries') and 'GB' in topic['countries']:
                # Replace GB with UK in the array
                new_countries = [c if c != 'GB' else 'UK' for c in topic['countries']]
                supabase.table("mvp2_megatopics").update({"countries": new_countries}).eq("id", topic['id']).execute()
                updated_count += 1
        
        print(f"  ✅ Updated {updated_count} megatopics with GB in countries array")
        
    except Exception as e:
        print(f"  ⚠️  Error updating megatopics countries: {e}")
    
    print(f"\n✨ Migration complete! Total rows updated: {total_updated}")

if __name__ == "__main__":
    migrate_gb_to_uk()
