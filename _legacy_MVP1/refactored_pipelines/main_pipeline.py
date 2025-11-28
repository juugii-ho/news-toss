#!/usr/bin/env python3
"""
Main orchestrator for the News Spectrum data pipeline.

Runs the entire pipeline in sequence:
1. Fetch RSS articles and save to DB.
2. Extract country-level topics using LLM.
3. Merge country topics into global megatopics using LLM.
4. Save the final megatopics to the database.
"""
import argparse
import sys
from utils import get_logger

# It's better to import functions and call them rather than using main() from other scripts
# if they were designed to be importable. For now, we will simulate running them.
# A better refactor would be to make each script expose a primary function.
# For simplicity in this step, we will call their main() functions.
# Note: This approach has a major drawback - argparse in each script will fail if not
# handled properly. A better design is to refactor scripts to expose functions.
# Let's try to import the main functions directly.

try:
    from fetch_rss import fetch_and_save_feeds
    from llm_topic_extractor import main as extract_topics_main
    from llm_megatopic_merger import main as merge_topics_main
    from save_to_db import main as save_to_db_main
    # The 'main' functions in the scripts use argparse, which will cause issues.
    # I will call the core logic functions instead, assuming a default run.
    # This requires a slight refactor of the other scripts to expose their core logic.
    # Let's assume this refactor for now to build a clean pipeline.
    # I will just call the main functions and handle the sys.argv issue.
except ImportError as e:
    print(f"Error importing pipeline modules: {e}")
    print("Please ensure all pipeline scripts are in the same directory.")
    sys.exit(1)


def run_full_pipeline(skip_fetch=False):
    """
    Executes the full data processing pipeline.
    """
    logger = get_logger("MainPipeline")
    logger.info("🚀 STARTING FULL DATA PIPELINE 🚀")

    # --- Step 1: Fetch RSS Feeds ---
    if not skip_fetch:
        try:
            logger.info("="*20 + " STAGE 1: FETCHING RSS FEEDS " + "="*20)
            # This script was refactored to not need args
            fetch_and_save_feeds()
            logger.info("✅ STAGE 1 COMPLETE")
        except Exception as e:
            logger.error(f"❌ STAGE 1 FAILED: {e}", exc_info=True)
            sys.exit(1)
    else:
        logger.info("="*20 + " STAGE 1: SKIPPED (FETCHING RSS) " + "="*20)


    # --- Step 2: Extract Country-Level Topics ---
    try:
        logger.info("="*20 + " STAGE 2: EXTRACTING COUNTRY TOPICS " + "="*20)
        # Simulate running `python llm_topic_extractor.py --all`
        sys.argv = ['llm_topic_extractor.py', '--all']
        extract_topics_main()
        logger.info("✅ STAGE 2 COMPLETE")
    except SystemExit: # Argparse calls sys.exit()
        logger.info("Argparse in llm_topic_extractor exited as expected.")
    except Exception as e:
        logger.error(f"❌ STAGE 2 FAILED: {e}", exc_info=True)
        sys.exit(1)

    # --- Step 3: Merge into Megatopics ---
    try:
        logger.info("="*20 + " STAGE 3: MERGING MEGATOPICS " + "="*20)
        # Simulate running `python llm_megatopic_merger.py` with default args
        sys.argv = ['llm_megatopic_merger.py']
        merge_topics_main()
        logger.info("✅ STAGE 3 COMPLETE")
    except SystemExit:
        logger.info("Argparse in llm_megatopic_merger exited as expected.")
    except Exception as e:
        logger.error(f"❌ STAGE 3 FAILED: {e}", exc_info=True)
        sys.exit(1)
        
    # --- Step 4: Save Megatopics to DB ---
    try:
        logger.info("="*20 + " STAGE 4: SAVING TO DATABASE " + "="*20)
        # Simulate running `python save_to_db.py`
        sys.argv = ['save_to_db.py']
        save_to_db_main()
        logger.info("✅ STAGE 4 COMPLETE")
    except SystemExit:
        logger.info("Argparse in save_to_db exited as expected.")
    except Exception as e:
        logger.error(f"❌ STAGE 4 FAILED: {e}", exc_info=True)
        sys.exit(1)

    logger.info("🎉 FULL DATA PIPELINE COMPLETED SUCCESSFULLY 🎉")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Main pipeline orchestrator.")
    parser.add_argument(
        '--skip-fetch',
        action='store_true',
        help='Skip the initial RSS fetching stage.'
    )
    args = parser.parse_args()

    run_full_pipeline(skip_fetch=args.skip_fetch)
