import os
from supabase import create_client

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(url, key)

try:
    # 1. Get local topics with categories
    response = supabase.table("mvp2_topics") \
        .select("id, category") \
        .neq("category", "null") \
        .limit(100) \
        .execute()

    if not response.data:
        print("No local topics with categories found.")
        exit(0)

    local_topic_ids = [t['id'] for t in response.data]

    # 2. Find articles linking these local topics to global topics
    response_articles = supabase.table("mvp2_articles") \
        .select("global_topic_id, local_topic_id") \
        .in_("local_topic_id", local_topic_ids) \
        .not_.is_("global_topic_id", "null") \
        .limit(100) \
        .execute()

    if response_articles.data:
        print("Found global topics with categorized local topics:")
        seen = set()
        for article in response_articles.data:
            gid = article['global_topic_id']
            if gid not in seen:
                print(f"Global Topic ID: {gid}")
                seen.add(gid)
                if len(seen) >= 3: break
    else:
        print("No linking articles found.")

except Exception as e:
    print(f"Error: {e}")
