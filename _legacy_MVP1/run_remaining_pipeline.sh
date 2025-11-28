#!/bin/bash
PYTHON_PATH="/Users/sml/anaconda3/envs/supabase_project/bin/python"

echo "----------------------------------------"
echo "4. Classifying Stance..."
$PYTHON_PATH data/pipelines/classify_stance.py

echo "----------------------------------------"
echo "5. Clustering Topics..."
$PYTHON_PATH data/pipelines/cluster_topics_vector.py

echo "----------------------------------------"
# 5. Aggregate Megatopics (Global)
echo "Aggregating megatopics..."
$PYTHON_PATH data/pipelines/aggregate_megatopics.py

# 6. Match Topics Across Days (Topic Drift)
echo "Matching topics across days..."
$PYTHON_PATH data/pipelines/match_topics_across_days.py

# 7. Visualize (Optional)
echo "Visualizing..."
$PYTHON_PATH data/pipelines/visualize_article_map.py

echo "----------------------------------------"
echo "✅ Remaining Pipeline Completed Successfully!"
