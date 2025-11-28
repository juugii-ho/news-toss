#!/bin/bash

# Load environment variables if needed (though python scripts load .env)
# export $(grep -v '^#' .env.local | xargs)

echo "🚀 Starting News Spectrum Pipeline..."

echo "----------------------------------------"
echo "1. Fetching RSS Feeds..."
/Users/sml/anaconda3/envs/supabase_project/bin/python data/pipelines/fetch_rss.py

echo "----------------------------------------"
echo "2. Translating Articles (EN/KR)..."
/Users/sml/anaconda3/envs/supabase_project/bin/python data/pipelines/translate_articles.py

echo "----------------------------------------"
echo "3. Generating Embeddings..."
/Users/sml/anaconda3/envs/supabase_project/bin/python data/pipelines/embed_articles.py

echo "----------------------------------------"
echo "4. Classifying Stance..."
/Users/sml/anaconda3/envs/supabase_project/bin/python data/pipelines/classify_stance.py

echo "----------------------------------------"
echo "5. Clustering Topics..."
/Users/sml/anaconda3/envs/supabase_project/bin/python data/pipelines/cluster_topics_vector.py

echo "----------------------------------------"
# 5. Aggregate Megatopics (Global)
echo "Aggregating megatopics..."
/Users/sml/anaconda3/envs/supabase_project/bin/python data/pipelines/aggregate_megatopics.py

# 6. Match Topics Across Days (Topic Drift)
echo "Matching topics across days..."
/Users/sml/anaconda3/envs/supabase_project/bin/python data/pipelines/match_topics_across_days.py

# 7. Visualize (Optional)
echo "Visualizing..."
/Users/sml/anaconda3/envs/supabase_project/bin/python data/pipelines/visualize_article_map.py

echo "----------------------------------------"
echo "✅ Pipeline Completed Successfully!"
