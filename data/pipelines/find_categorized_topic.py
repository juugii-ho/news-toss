import os
from supabase import create_client

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(url, key)

try:
    response = supabase.table("mvp2_global_topics") \
        .select("id, title_ko, category") \
        .neq("category", "null") \
        .limit(5) \
        .execute()

    if response.data:
        print("Found topics with category:")
        for topic in response.data:
            if topic.get('category'):
                print(f"ID: {topic['id']}")
                print(f"Title: {topic['title_ko']}")
                print(f"Category: {topic['category']}")
                print("-" * 20)
                break # Just need one
    else:
        print("No topics found with a category.")

except Exception as e:
    print(f"Error: {e}")
