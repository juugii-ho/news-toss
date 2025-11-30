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
    response = supabase.table("mvp2_topics") \
        .select("id, topic_name, category") \
        .eq("global_topic_id", global_topic_id) \
        .execute()

    if response.data:
        print(f"Local topics for global topic {global_topic_id}:")
        for topic in response.data:
            print(f"ID: {topic['id']}")
            print(f"Name: {topic['topic_name']}")
            print(f"Category: {topic['category']}")
            print("-" * 20)
    else:
        print("No local topics found for this global topic.")

except Exception as e:
    print(f"Error: {e}")
