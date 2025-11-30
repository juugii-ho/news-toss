import subprocess
import sys
import time
import os

def run_step(script_name, description):
    print(f"\n{'='*60}")
    print(f"🚀 [Step] {description}")
    print(f"   Running: {script_name}")
    print(f"{'='*60}\n")
    
    start_time = time.time()
    
    # Calculate absolute path to the script
    # This script is in data/pipelines/run_full_pipeline.py
    # So the project root is 2 levels up
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    
    # Target script path
    script_path = os.path.join(current_dir, script_name)
    
    try:
        # Run with cwd set to project root to ensure imports work if needed
        # But wait, the scripts inside data/pipelines might expect to be run from root 
        # or have their own relative path logic.
        # Most scripts in this repo seem to assume CWD is project root.
        
        cmd = [sys.executable, script_path]
        
        subprocess.run(cmd, check=True, cwd=project_root)
        
        elapsed = time.time() - start_time
        print(f"\n✅ Step Completed in {elapsed:.2f} seconds.")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Step Failed: {e}")
        print("Stopping pipeline.")
        sys.exit(1)

def main():
    print("🌟 Starting News Spectrum Full Pipeline (Local Run) 🌟")
    print(f"Python Executable: {sys.executable}")
    
    # 1. RSS Collection
    run_step("rss_collector.py", "Fetching latest articles from RSS feeds")
    
    # 2. Translation
    run_step("llm_translator.py", "Translating titles (KR/EN) using Gemini")
    
    # 3. Clustering (Country Level)
    run_step("run_all_clustering.py", "Clustering articles by country (Last 24h)")
    
    # 4. Enrichment (Source Deduplication)
    # Using parallel version for speed
    run_step("run_all_enrichment_parallel.py", "Deduplicating sources and enriching topics")
    
    # 5. Global Megatopic Analysis
    run_step("llm_megatopic_analysis.py", "Generating Global Megatopics and Saving to DB")
    
    print(f"\n{'='*60}")
    print("🎉 PIPELINE COMPLETED SUCCESSFULLY! 🎉")
    print("   - Articles Collected & Translated")
    print("   - Local Topics Saved to DB (mvp2_topics)")
    print("   - Global Megatopics Saved to DB (mvp2_megatopics)")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
