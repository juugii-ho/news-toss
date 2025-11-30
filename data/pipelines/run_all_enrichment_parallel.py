import subprocess
import time
import sys
import os

COUNTRIES = ['AU', 'BE', 'CA', 'CN', 'DE', 'FR', 'GB', 'IT', 'JP', 'KR', 'NL', 'RU', 'US']
MAX_CONCURRENT = 10

def main():
    print(f"🚀 Starting Parallel Enrichment for {len(COUNTRIES)} countries (Max {MAX_CONCURRENT} concurrent)...")
    
    processes = []
    queue = COUNTRIES[:]
    
    while queue or processes:
        # Start new processes if slots available
        while len(processes) < MAX_CONCURRENT and queue:
            country = queue.pop(0)
            print(f"  ✨ Starting {country}...")
            # Use absolute path to ensure it works from any directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            enrichment_script = os.path.join(script_dir, "llm_topic_enrichment.py")
            
            cmd = [sys.executable, enrichment_script, country]
            p = subprocess.Popen(cmd)
            processes.append((country, p))
            
        # Check for completed processes
        active_processes = []
        for country, p in processes:
            if p.poll() is not None: # Process finished
                if p.returncode == 0:
                    print(f"  ✅ {country} Completed.")
                else:
                    print(f"  ❌ {country} Failed with code {p.returncode}.")
            else:
                active_processes.append((country, p))
                
        processes = active_processes
        time.sleep(1) # Check every second

    print("\n🎉 All countries enriched.")

if __name__ == "__main__":
    main()
