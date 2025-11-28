import os
import random
import numpy as np
from datetime import datetime, timedelta
from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path

# Load environment
root_dir = Path(__file__).resolve().parent
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def simulate_history():
    print("Fetching today's history...")
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    res = supabase.table("mvp_topic_history").select("*").eq("date", today_str).execute()
    today_records = res.data
    
    if not today_records:
        print("No records for today to simulate from.")
        return
        
    print(f"Found {len(today_records)} records. Simulating past 3 days...")
    
    new_records = []
    
    for i in range(1, 4): # 1, 2, 3 days ago
        past_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        print(f"  Simulating for {past_date}...")
        
        # Check if exists
        check = supabase.table("mvp_topic_history").select("id").eq("date", past_date).limit(1).execute()
        if check.data:
            print(f"    Records already exist for {past_date}. Skipping.")
            continue
            
        for rec in today_records:
            # Clone and mutate
            new_rec = rec.copy()
            del new_rec['id'] # Let DB assign ID
            del new_rec['created_at']
            new_rec['date'] = past_date
            
            # Mutate score slightly
            if new_rec['avg_stance_score'] is not None:
                change = random.uniform(-10, 10)
                new_rec['avg_stance_score'] = max(0, min(100, new_rec['avg_stance_score'] + change))
                
            # Mutate intensity
            if new_rec['intensity']:
                new_rec['intensity'] = max(1, int(new_rec['intensity'] * random.uniform(0.8, 1.2)))
                
            # Mutate drift
            new_rec['drift_score'] = random.uniform(0.01, 0.2)
            
            # Reset new flag
            new_rec['is_new_topic'] = False
            
            new_records.append(new_rec)
            
    if new_records:
        print(f"Inserting {len(new_records)} simulated records...")
        # Insert in batches
        batch_size = 50
        for i in range(0, len(new_records), batch_size):
            batch = new_records[i:i+batch_size]
            try:
                supabase.table("mvp_topic_history").insert(batch).execute()
            except Exception as e:
                print(f"Error inserting batch: {e}")
    else:
        print("No new records to insert.")
        
    print("Done.")

if __name__ == "__main__":
    simulate_history()
