import subprocess
import sys
import time
import os
import argparse

def run_step(script_name, description, args=None, allow_failure=False):
    print(f"\n{'='*80}")
    print(f"🚀 [Step] {description}")
    print(f"   Running: {script_name} {' '.join(args) if args else ''}")
    print(f"{'='*80}\n")
    
    start_time = time.time()
    
    # Calculate absolute path to the script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    script_path = os.path.join(current_dir, script_name)
    
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
        
    try:
        # Run with cwd set to project root
        subprocess.run(cmd, check=True, cwd=project_root)
        
        elapsed = time.time() - start_time
        print(f"\n✅ Step Completed in {elapsed:.2f} seconds.")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Step Failed: {e}")
        if allow_failure:
            print("⚠️ Warning: Step failed but pipeline will continue (allow_failure=True).")
            return False
        else:
            print("⛔ Critical Error: Stopping pipeline.")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Run the Unified News Spectrum Pipeline")
    parser.add_argument("--skip-rss", action="store_true", help="Skip RSS collection and translation")
    args = parser.parse_args()

    print("🌟 Starting News Spectrum UNIFIED Pipeline 🌟")
    print(f"Python Executable: {sys.executable}")
    
    total_start = time.time()

    # 1. RSS Collection
    if not args.skip_rss:
        run_step("rss_collector.py", "Fetching latest articles from RSS feeds")
    else:
        print("⏩ Skipping RSS Collection (--skip-rss)")

    # 2. Translation
    if not args.skip_rss:
        run_step("llm_translator.py", "Translating titles (KR/EN)")
    else:
        print("⏩ Skipping Translation (--skip-rss)")

    # 3. Clustering (Country Level)
    # This script handles parallel execution internally
    run_step("run_all_clustering.py", "Clustering articles by country (Last 24h)")
    
    # 4. Enrichment (Source Deduplication & Topic Generation)
    # This script handles parallel execution internally
    run_step("run_all_enrichment_parallel.py", "Enriching topics (LLM Analysis)")
    
    # 5. Global Megatopic Analysis
    run_step("llm_megatopic_analysis.py", "Generating Global Megatopics")

    # 6. Local Topic Summaries
    # Generates summaries for local topics that missed them
    run_step("llm_topic_summary_generator.py", "Generating Local Topic Summaries", allow_failure=True)

    # 7. Global Editor Comments
    # CRITICAL: Using --all and --threshold 2 as requested
    run_step("llm_global_editor_comment_generator.py", "Generating Global Editor Comments", 
             args=["--all", "--threshold", "2"], allow_failure=True)

    # 8. Local Thumbnails
    run_step("llm_thumbnail_generator.py", "Generating Local Thumbnails", allow_failure=True)
    
    # 9. Global Thumbnails
    run_step("llm_global_thumbnail_generator.py", "Generating Global Thumbnails", allow_failure=True)
    
    # 10. Publish
    # Atomically publishes everything created in the last 24h
    run_step("publish_batch.py", "Publishing Batch to Live")
    
    total_elapsed = time.time() - total_start
    print(f"\n{'='*80}")
    print(f"🎉 UNIFIED PIPELINE COMPLETED SUCCESSFULLY! 🎉")
    print(f"⏱️ Total Time: {total_elapsed/60:.2f} minutes")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
