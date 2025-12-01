
import os
from dotenv import load_dotenv
from supabase import create_client
from collections import Counter

load_dotenv('backend/.env')

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase = create_client(url, key)

print("--- 🔍 Inspecting Published Global Megatopics ---")
res_mega = supabase.table("mvp2_megatopics")\
    .select("id, name, created_at, batch_id")\
    .eq("is_published", True)\
    .order("created_at", desc=True)\
    .execute()

mega_names = [r['name'] for r in res_mega.data]
mega_batches = [r['batch_id'] for r in res_mega.data]

print(f"Total Published Megatopics: {len(res_mega.data)}")
print(f"Unique Names: {len(set(mega_names))}")
print(f"Unique Batches: {set(mega_batches)}")

# Check for duplicates
name_counts = Counter(mega_names)
dupes = {k: v for k, v in name_counts.items() if v > 1}
if dupes:
    print(f"\n⚠️ DUPLICATE Megatopics Found ({len(dupes)}):")
    for name, count in list(dupes.items())[:10]:
        print(f"  - {name}: {count} times")
else:
    print("\n✅ No duplicate Megatopic names.")


print("\n--- 🔍 Inspecting Published KR Topics ---")
res_topics = supabase.table("mvp2_topics")\
    .select("id, topic_name, created_at, batch_id")\
    .eq("country_code", "KR")\
    .eq("is_published", True)\
    .order("created_at", desc=True)\
    .execute()

topic_names = [r['topic_name'] for r in res_topics.data]
topic_batches = [r['batch_id'] for r in res_topics.data]

print(f"Total Published KR Topics: {len(res_topics.data)}")
print(f"Unique Names: {len(set(topic_names))}")
print(f"Unique Batches: {set(topic_batches)}")

# Check for duplicates
topic_counts = Counter(topic_names)
topic_dupes = {k: v for k, v in topic_counts.items() if v > 1}
if topic_dupes:
    print(f"\n⚠️ DUPLICATE KR Topics Found ({len(topic_dupes)}):")
    for name, count in list(topic_dupes.items())[:10]:
        print(f"  - {name}: {count} times")
else:
    print("\n✅ No duplicate KR Topic names.")

print("\n--- 🔍 Sample Duplicate Detail (if any) ---")
if topic_dupes:
    target_name = list(topic_dupes.keys())[0]
    print(f"Details for '{target_name}':")
    details = [r for r in res_topics.data if r['topic_name'] == target_name]
    for d in details:
        print(f"  - ID: {d['id']}, Created: {d['created_at']}, Batch: {d['batch_id']}")
