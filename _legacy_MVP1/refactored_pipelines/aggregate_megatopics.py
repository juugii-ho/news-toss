import json
import numpy as np
import os
import requests
import time
from datetime import datetime, timezone, timedelta
from collections import Counter
from dotenv import load_dotenv
from pathlib import Path
from supabase import create_client

# Load environment variables
root_dir = Path(__file__).resolve().parents[2]
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") # Use Service Role Key for writing
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def generate_topic_summary(title, articles):
    """Generate a concise 2-sentence summary of the megatopic."""
    if not GEMINI_API_KEY:
        return f"Global megatopic involving {len(articles)} articles."
        
    try:
        # Use first 5 article summaries/titles as context
        context = "\n".join([f"- {a['title']}: {(a.get('summary') or '')[:100]}" for a in articles[:5]])
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        prompt = f"""Summarize the following news topic into 2 concise sentences in English.
        Topic: {title}
        Context:
        {context}
        """
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.ok:
            result = response.json()
            if result and 'candidates' in result and result['candidates']:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    return candidate['content']['parts'][0]['text'].strip()
    except Exception as e:
        print(f"Summary generation failed: {e}")
        
    return f"Global megatopic involving {len(articles)} articles."

def batch_translate_to_korean(texts, retries=3):
    """
    Translates a list of English texts to Korean using Gemini API.
    """
    if not GEMINI_API_KEY:
        return texts
        
    BATCH_SIZE = 50
    all_translations = []
    
    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i:i+BATCH_SIZE]
        
        prompt = """You are a professional news translator. Translate the following English headlines/summaries into natural Korean.
        Keep the tone professional and objective.
        Output ONLY the translated lines in the same order, one per line.
        
        Texts:
        """ + "\n".join([f"- {t}" for t in batch_texts])
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        
        batch_results = []
        for attempt in range(retries):
            try:
                response = requests.post(url, headers=headers, json=data, timeout=300)
                if response.ok:
                    result = response.json()
                    if result and 'candidates' in result and result['candidates']:
                        content = result['candidates'][0]['content']['parts'][0]['text'].strip()
                        for line in content.split('\n'):
                            line = line.strip()
                            if line and (line[0].isdigit() or line.startswith('-')):
                                cleaned = line.split('.', 1)[-1].strip() if '.' in line else line.strip('- ')
                                batch_results.append(cleaned)
                        break
            except Exception as e:
                print(f"Error translating batch: {e}")
                time.sleep(2 ** attempt)
        
        if not batch_results:
            batch_results = batch_texts
            
        # Pad or truncate
        if len(batch_results) < len(batch_texts):
            batch_results.extend(batch_texts[len(batch_results):])
        elif len(batch_results) > len(batch_texts):
            batch_results = batch_results[:len(batch_texts)]
            
        all_translations.extend(batch_results)
        time.sleep(1)
        
    return all_translations

def cosine_similarity_manual(v1, v2):
    if not v1 or not v2: return 0
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0: return 0
    return dot_product / (norm_v1 * norm_v2)

from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def aggregate_megatopics(clusters):
    print(f"Aggregating {len(clusters)} clusters...")
    
    # 0. Fetch existing recent topics to deduplicate against
    print("Fetching existing recent topics for deduplication...")
    existing_topics = []
    try:
        # Fetch topics from last 72 hours (3 days)
        # This defines the "Lifecycle" of a topic. If it's older than 3 days and goes dormant,
        # a new recurrence will start a new topic.
        three_days_ago = (datetime.now(timezone.utc) - timedelta(hours=72)).isoformat()
        
        res = supabase.table("mvp_topics") \
            .select("id, title, centroid_embedding, country_count, created_at") \
            .gte("created_at", three_days_ago) \
            .order("id", desc=True) \
            .execute()
        
        for t in res.data:
            if t.get('centroid_embedding') and isinstance(t['centroid_embedding'], str):
                try:
                    t['centroid_embedding'] = json.loads(t['centroid_embedding'])
                except:
                    t['centroid_embedding'] = None
            existing_topics.append(t)
        print(f"Loaded {len(existing_topics)} existing topics from last 72h.")
    except Exception as e:
        print(f"Error fetching existing topics: {e}")

    megatopics_to_save = []
    
    for cluster in clusters:
        # 1. Identify countries involved
        countries = set(a['country_code'] for a in cluster)
        
        # Filter: Must be a "Megatopic"
        is_global = len(countries) >= 3
        is_major_national = len(countries) == 1 and len(cluster) >= 5
        
        if not (is_global or is_major_national):
            continue
            
        # Determine representative title using TF-IDF
        # Avoid selecting overly long "LIVE news" aggregate titles
        from collections import Counter
        import re
        
        def tokenize(text):
            # Simple tokenization: lowercase, remove punctuation, split
            return re.findall(r'\b[a-z]{3,}\b', text.lower())
        
        # Calculate term frequency across all titles
        all_words = []
        title_words = []
        for article in cluster:
            title_text = article.get('title_en', article['title'])
            words = tokenize(title_text)
            title_words.append((article, words))
            all_words.extend(words)
        
        # IDF: inverse document frequency
        word_counts = Counter(all_words)
        num_docs = len(cluster)
        
        # Score each title
        best_title = None
        best_score = -1
        
        for article, words in title_words:
            if not words:
                continue
            
            # TF-IDF score
            tf_idf_score = sum(word_counts[w] / num_docs for w in set(words))
            
            # Penalize overly long titles (likely "LIVE news" aggregates)
            title_len = len(article.get('title_en', article['title']))
            length_penalty = 1.0
            if title_len > 150:  # Titles longer than 150 chars get penalty
                length_penalty = 0.5
            elif title_len > 100:
                length_penalty = 0.8
            
            final_score = tf_idf_score * length_penalty
            
            if final_score > best_score:
                best_score = final_score
                best_title = article
        
        # Fallback to first article if TF-IDF fails
        if best_title is None:
            best_title = cluster[0]
        
        title_text = best_title.get('title_en', best_title['title'])
        
        # Calculate Centroid Embedding
        embeddings = [a['embedding'] for a in cluster if a.get('embedding')]
        centroid = []
        if embeddings:
            centroid = np.mean(embeddings, axis=0).tolist()
            
        # DEDUPLICATION CHECK
        match_found = False
        matched_topic_id = None
        
        # Check against existing topics (DB) AND newly created ones (megatopics_to_save)
        # We need to check both because we might have just created a topic in this run
        
        # Combine lists for checking
        all_candidates = existing_topics + megatopics_to_save
        
        for candidate in all_candidates:
            # 1. Title Fuzzy Match
            title_sim = similar(title_text.lower(), candidate['title'].lower())
            
            # 2. Semantic Match
            semantic_sim = 0
            if centroid and candidate.get('centroid_embedding'):
                semantic_sim = cosine_similarity_manual(centroid, candidate['centroid_embedding'])
                
            # Thresholds (Phase 1 Fix - 2025-11-27) 
            # UPDATED: Title lowered to 0.75 after finding many 0.75-0.85 duplicates
            # Korean translations often have slight variations that score 0.75-0.85
            # Changed from OR to AND: Both title AND semantic must match
            # Title: 0.85 → 0.75 (catch Korean variant translations)
            # Semantic: 0.92 → 0.88 (allow same event different wording)
            if title_sim > 0.75 and semantic_sim > 0.85:
                print(f"Duplicate found! '{title_text}' matches '{candidate['title']}' (Title: {title_sim:.2f}, Semantic: {semantic_sim:.2f})")
                match_found = True
                matched_topic_id = candidate.get('id') # Only exists for DB topics
                
                # If it's a DB topic, we update it immediately
                if matched_topic_id:
                    print(f"Updating existing topic {matched_topic_id}...")
                    try:
                        # 1. Save CURRENT state to history (Snapshot for Drift)
                        # We need to fetch the current full state first
                        current_topic = candidate # We already have it from the fetch above
                        
                        history_entry = {
                            "topic_id": matched_topic_id,
                            "date": datetime.now(timezone.utc).isoformat(), # Timestamp of this snapshot
                            # article_count doesn't exist in mvp_topics table
                            "country_count": current_topic['country_count'],
                            "centroid_embedding": current_topic['centroid_embedding']
                        }
                        
                        supabase.table("mvp_topic_history").insert(history_entry).execute()
                        
                        # 2. Update Topic Stats & Centroid
                        # Calculate new combined stats
                        # This is an approximation. Ideally we re-calculate from all articles.
                        # For now, we'll just update the centroid and let stats be recalculated elsewhere
                        # Blending centroids: (N1*C1 + N2*C2) / (N1+N2)
                        
                        new_articles_count = len(cluster)
                        # article_count doesn't exist in DB, calculate from stats if needed
                        # For now just use the new cluster size for centroid blending
                        old_articles_count = new_articles_count  # Approximate, doesn't affect much
                        total_count = old_articles_count + new_articles_count
                        
                        new_centroid = centroid
                        old_centroid = current_topic['centroid_embedding']
                        
                        # Blend centroids
                        if old_centroid and new_centroid:
                            updated_centroid = [
                                (old_articles_count * o + new_articles_count * n) / total_count
                                for o, n in zip(old_centroid, new_centroid)
                            ]
                        else:
                            updated_centroid = new_centroid or old_centroid
                        
                        # Update topic record (removed article_count field)
                        supabase.table("mvp_topics").update({
                            "centroid_embedding": updated_centroid,
                            # We could update country_count here too if we fetched old countries
                        }).eq("id", matched_topic_id).execute()

                        # 3. Update articles to point to this topic
                        article_ids = [a['id'] for a in cluster if 'id' in a]
                        if article_ids:
                            supabase.table("mvp_articles") \
                                .update({"topic_id": matched_topic_id}) \
                                .in_("id", article_ids) \
                                .execute()
                                
                        # 4. Update Country Stats (Insert new ones or update existing)
                        # This is tricky without fetching old stats. 
                        # For MVP, let's just INSERT new stats for the new articles.
                        # If a country already exists, we should ideally increment.
                        # But `mvp_topic_country_stats` is (topic_id, country_code) unique?
                        # Let's check if we can upsert or if we need to fetch.
                        # For now, let's skip complex stat merging to avoid errors, 
                        # assuming the main value is the article link.
                        
                    except Exception as e:
                        print(f"Error updating topic {matched_topic_id}: {e}")
                else:
                    # It matched a topic in `megatopics_to_save` (not yet in DB)
                    # We should merge this cluster into that pending topic
                    # For simplicity, we'll just skip creating a NEW topic, 
                    # but we should ideally add these articles to that pending topic's article list.
                    # Find the pending topic object
                    for pt in megatopics_to_save:
                        if pt['title'] == candidate['title']:
                            pt['articles'].extend(cluster)
                            pt['countries_involved'] = list(set(pt['countries_involved']) | countries)
                            pt['article_count'] += len(cluster)
                            break
                break
        
        if match_found:
            continue

        # If no match, create new topic
        stats = {}
        for cc in countries:
            country_articles = [a for a in cluster if a['country_code'] == cc]
            stances = [(a.get('stance') or 'factual') for a in country_articles]
            counts = Counter(stances)
            stats[cc] = {
                "supportive": counts.get('supportive', 0),
                "factual": counts.get('factual', 0),
                "critical": counts.get('critical', 0),
                "avg_score": int(sum(a.get('stance_score', 50) or 50 for a in country_articles) / len(country_articles)) if country_articles else 50
            }
            
        summary = generate_topic_summary(title_text, cluster)
            
        megatopics_to_save.append({
            "title": title_text,
            "date": datetime.now(timezone.utc).isoformat(),
            "countries_involved": list(countries),
            "article_count": len(cluster),
            "stats": stats,
            "summary": summary,
            "centroid_embedding": centroid,
            "articles": cluster
        })
        
        if len(megatopics_to_save) >= 50: # Increased limit
            break
            
    return megatopics_to_save

def save_to_supabase(megatopics):
    print(f"Saving {len(megatopics)} megatopics to Supabase...")
    
    for topic in megatopics:
        try:
            # 1. Insert Topic
            topic_data = {
                "title": topic['title'],
                "title_kr": topic.get('title_kr', topic['title']),
                "date": topic['date'],
                "summary": topic.get('summary', ""),
                "divergence_score": 0.0,
                "country_count": len(topic['countries_involved']),
                "centroid_embedding": topic.get('centroid_embedding') # Save embedding
            }
            
            res = supabase.table("mvp_topics").insert(topic_data).execute()
            if not res.data:
                print(f"Failed to insert topic: {topic['title']}")
                continue
                
            topic_id = res.data[0]['id']
            
            # 2. Insert Stats
            stats_data = []
            for country_code, counts in topic['stats'].items():
                # Calculate unique sources for this country in this topic
                country_articles = [a for a in topic['articles'] if a.get('country_code') == country_code]
                unique_sources = len(set(a.get('source', '') for a in country_articles if a.get('source')))
                
                stats_data.append({
                    "topic_id": topic_id,
                    "country_code": country_code,
                    "supportive_count": counts['supportive'],
                    "factual_count": counts['factual'],
                    "critical_count": counts['critical'],
                    "avg_score": counts.get('avg_score', 50),
                    "source_count": unique_sources  # Add source diversity metric
                })
                
            if stats_data:
                supabase.table("mvp_topic_country_stats").insert(stats_data).execute()

            # 3. Update Articles (Link to Topic)
            # We assume articles already exist in DB (from fetch_rss.py)
            # We just need to update their topic_id
            if 'articles' in topic:
                article_ids = [a['id'] for a in topic['articles'] if 'id' in a]
                if article_ids:
                    # Update in batches if needed, but for < 100 articles, one call is fine?
                    # Supabase update with 'in' filter
                    supabase.table("mvp_articles") \
                        .update({"topic_id": topic_id}) \
                        .in_("id", article_ids) \
                        .execute()
                
        except Exception as e:
            print(f"Error saving topic '{topic['title']}': {e}")

if __name__ == "__main__":
    try:
        # Read from clustered_topics.json (produced by cluster_topics_vector.py)
        # This file now contains full article objects from DB
        input_file = root_dir / "data/pipelines/clustered_topics.json"
        if not input_file.exists():
             print("clustered_topics.json not found.")
             exit(1)
             
        with open(input_file, "r") as f:
            clusters = json.load(f)
            
        final_megatopics = aggregate_megatopics(clusters)
        
        print(f"Identified {len(final_megatopics)} global megatopics.")
        
        # Batch Translate Titles
        titles_to_translate = [t['title'] for t in final_megatopics]
        if titles_to_translate:
            print(f"Translating {len(titles_to_translate)} titles to Korean...")
            translated_titles = batch_translate_to_korean(titles_to_translate)
            
            for i, kr_title in enumerate(translated_titles):
                final_megatopics[i]['title_kr'] = kr_title

        # Save to Supabase
        save_to_supabase(final_megatopics)
            
    except Exception as e:
        print(f"Error in aggregation: {e}")
