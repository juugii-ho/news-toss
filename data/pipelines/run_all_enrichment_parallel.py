import subprocess
import sys
import os
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

COUNTRIES = ['AU', 'BE', 'CA', 'CN', 'DE', 'FR', 'GB', 'IT', 'JP', 'KR', 'NL', 'RU', 'US']
MAX_WORKERS = 10

def run_enrichment(country, batch_id):
    """Run enrichment for a single country"""
    print(f"  ✨ Starting {country}...")
    try:
        # Pass batch_id as argument
        result = subprocess.run(
            [sys.executable, "data/pipelines/llm_topic_enrichment.py", country, f"--batch_id={batch_id}"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"  ✅ {country} Completed.")
            return True
        else:
            print(f"  ❌ {country} Failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ {country} Error: {e}")
        return False

def main():
    # Generate a shared batch_id for this entire run
    SHARED_BATCH_ID = str(uuid.uuid4())
    print(f"🚀 Starting Parallel Enrichment for {len(COUNTRIES)} countries (Max {MAX_WORKERS} concurrent)...")
    print(f"🔖 Shared Batch ID: {SHARED_BATCH_ID}")
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks with shared batch_id
        future_to_country = {executor.submit(run_enrichment, country, SHARED_BATCH_ID): country for country in COUNTRIES}
        
        for future in as_completed(future_to_country):
            country = future_to_country[future]
            try:
                success = future.result()
            except Exception as exc:
                print(f"  ❌ {country} generated an exception: {exc}")

    print("\n🎉 All countries enriched.")

if __name__ == "__main__":
    main()
