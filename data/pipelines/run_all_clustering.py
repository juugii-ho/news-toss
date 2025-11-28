import subprocess
import time

COUNTRIES = ['AU', 'BE', 'CA', 'CN', 'DE', 'FR', 'GB', 'IT', 'JP', 'KR', 'NL', 'RU', 'US']

def main():
    print(f"🚀 Starting Global Clustering for {len(COUNTRIES)} countries...")
    
    for country in COUNTRIES:
        print(f"\n--------------------------------------------------")
        print(f"🌍 Processing Country: {country}")
        print(f"--------------------------------------------------")
        
        try:
            # Run the clustering script
            cmd = [sys.executable, "data/pipelines/llm_topic_clustering_embedding.py", country]
            subprocess.run(cmd, check=True)
            print(f"✅ {country} Completed.")
        except subprocess.CalledProcessError as e:
            print(f"❌ {country} Failed: {e}")
        
        time.sleep(1) # Brief pause between countries

    print("\n🎉 All countries processed.")

if __name__ == "__main__":
    main()
