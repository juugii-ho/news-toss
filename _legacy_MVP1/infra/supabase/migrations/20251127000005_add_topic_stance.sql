-- Add avg_stance_score to mvp_topics for easier visualization query
ALTER TABLE mvp_topics
ADD COLUMN IF NOT EXISTS avg_stance_score FLOAT;
