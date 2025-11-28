-- Fix stats directly via SQL (bypasses schema cache)

-- Insert stats for each topic/country combination
WITH topic_article_stats AS (
  SELECT 
    a.topic_id,
    a.country_code,
    COUNT(*) as article_count,
    COUNT(DISTINCT a.source) as source_count,
    SUM(CASE WHEN COALESCE(a.stance_score, 50) > 66 THEN 1 ELSE 0 END) as total_supportive,
    SUM(CASE WHEN COALESCE(a.stance_score, 50) BETWEEN 33 AND 66 THEN 1 ELSE 0 END) as total_factual,
    SUM(CASE WHEN COALESCE(a.stance_score, 50) < 33 THEN 1 ELSE 0 END) as total_critical
  FROM mvp_articles a
  INNER JOIN mvp_topics t ON a.topic_id = t.id
  WHERE t.extraction_method = 'llm'
    AND a.topic_id IS NOT NULL
  GROUP BY a.topic_id, a.country_code
)
INSERT INTO mvp_topic_country_stats (
  topic_id, country_code, article_count, source_count,
  total_supportive, total_factual, total_critical
)
SELECT 
  topic_id, country_code, article_count, source_count,
  total_supportive, total_factual, total_critical
FROM topic_article_stats
ON CONFLICT (topic_id, country_code) 
DO UPDATE SET
  article_count = EXCLUDED.article_count,
  source_count = EXCLUDED.source_count,
  total_supportive = EXCLUDED.total_supportive,
  total_factual = EXCLUDED.total_factual,
  total_critical = EXCLUDED.total_critical;

-- Verify
SELECT 
  t.id,
  t.title_kr,
  COUNT(DISTINCT s.country_code) as country_count,
  SUM(s.article_count) as total_articles
FROM mvp_topics t
LEFT JOIN mvp_topic_country_stats s ON t.id = s.topic_id
WHERE t.extraction_method = 'llm'
GROUP BY t.id, t.title_kr
ORDER BY t.id;
