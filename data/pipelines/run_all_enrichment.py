import subprocess
import time

COUNTRIES = ['AU', 'BE', 'CA', 'CN', 'DE', 'FR', 'GB', 'IT', 'JP', 'KR', 'NL', 'RU', 'US']

def main():
    print(f"🚀 Starting Global Enrichment for {len(COUNTRIES)} countries...")
    
    for country in COUNTRIES:
        print(f"\n--------------------------------------------------")
        print(f"✨ Enriching Country: {country}")
        print(f"--------------------------------------------------")
        
        try:
            # Run the enrichment script
            cmd = ["/Users/sml/gemini_env/bin/python", "data/pipelines/llm_topic_enrichment.py", country]
            subprocess.run(cmd, check=True)
            print(f"✅ {country} Completed.")
        except subprocess.CalledProcessError as e:
            print(f"❌ {country} Failed: {e}")
        
        time.sleep(1) # Brief pause between countries

    print("\n🎉 All countries enriched.")

if __name__ == "__main__":
    main()
