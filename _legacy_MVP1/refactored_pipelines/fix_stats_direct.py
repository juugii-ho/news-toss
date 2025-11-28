#!/usr/bin/env python3
"""
Fix stats using direct database connection (bypasses schema cache)
"""

import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

# Load environment
root_dir = Path(__file__).resolve().parents[2]
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")

if not DATABASE_URL:
    print("Error: DATABASE_URL not found in .env")
    print("Get it from Supabase Dashboard > Project Settings > Database > Connection String")
    exit(1)

print("Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print("Generating stats for LLM topics...")

sql = """
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
"""

cur.execute(sql)
conn.commit()

print(f"✅ Stats inserted/updated: {cur.rowcount} rows")

# Verify
cur.execute("""
SELECT 
  t.id,
  t.title_kr,
  COUNT(DISTINCT s.country_code) as country_count,
  SUM(s.article_count) as total_articles
FROM mvp_topics t
LEFT JOIN mvp_topic_country_stats s ON t.id = s.topic_id
WHERE t.extraction_method = 'llm'
GROUP BY t.id, t.title_kr
ORDER BY t.id
""")

print("\n검증 결과:")
print("="*80)
for row in cur.fetchall():
    topic_id, title_kr, country_count, total_articles = row
    print(f"ID {topic_id}: {title_kr}")
    print(f"  {country_count}개국, {total_articles}개 기사")

cur.close()
conn.close()

print("\n✅ 완료!")
