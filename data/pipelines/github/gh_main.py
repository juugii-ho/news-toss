import subprocess
import sys
import os
import time

def run_step(script_name, description):
    print(f"\n{'='*50}")
    print(f"🚀 Step: {description}")
    print(f"   Script: {script_name}")
    print(f"{'='*50}\n")
    
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
    
    start_time = time.time()
    try:
        # Run with unbuffered output
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=sys.stdout,
            stderr=sys.stderr,
            env=os.environ.copy()
        )
        process.wait()
        
        if process.returncode != 0:
            print(f"\n❌ Step failed with return code {process.returncode}")
            sys.exit(process.returncode)
            
    except Exception as e:
        print(f"\n❌ Error running step: {e}")
        sys.exit(1)
        
    elapsed = time.time() - start_time
    print(f"\n✅ Step completed in {elapsed:.1f}s")

def main():
    print("🌍 Starting News Spectrum Pipeline (GitHub Actions Mode)")
    print(f"   Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. RSS Collection
    run_step("gh_rss_collector.py", "RSS Feed Collection")
    
    # 2. Translation
    run_step("gh_translator.py", "Article Translation (KO/EN)")
    
    # 3. Clustering (Sequential)
    run_step("gh_clustering.py", "Topic Clustering & Stance Analysis")
    
    # 4. Enrichment (Deduplication & Stance Preservation)
    run_step("gh_enrichment.py", "Topic Enrichment & DB Sync")
    
    # 5. Megatopic Analysis
    run_step("gh_megatopic.py", "Global Megatopic Generation")

    # 6. Thumbnail Generation
    run_step("gh_thumbnail.py", "Thumbnail Generation")
    
    print(f"\n{'='*50}")
    print("🎉 Pipeline Completed Successfully!")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
