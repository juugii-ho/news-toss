import os
from supabase import create_client

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(url, key)
global_topic_id = "1344c17c-a98b-4a17-8a93-40ee1150081c"

try:
    # 1. Get articles linking to this global topic
    response_articles = supabase.table("mvp2_articles") \
        .select("local_topic_id") \
        .eq("global_topic_id", global_topic_id) \
        .not_.is_("local_topic_id", "null") \
        .execute()

    if not response_articles.data:
        print("No linked articles found.")
        exit(0)

    local_topic_ids = list(set([a['local_topic_id'] for a in response_articles.data]))
    print(f"Found {len(local_topic_ids)} linked local topics.")

    # 2. Get categories for these local topics
    response_topics = supabase.table("mvp2_topics") \
        .select("id, topic_name, category") \
        .in_("id", local_topic_ids) \
        .execute()

    if response_topics.data:
        for t in response_topics.data:
            print(f"ID: {t['id']}")
            print(f"Category: '{t['category']}' (Type: {type(t['category'])})")
    else:
        print("Could not fetch local topics.")

except Exception as e:
    print(f"Error: {e}")
