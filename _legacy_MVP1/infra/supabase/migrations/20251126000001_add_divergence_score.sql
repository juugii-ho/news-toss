-- Add divergence_score to mvp_topics table
ALTER TABLE mvp_topics 
ADD COLUMN IF NOT EXISTS divergence_score FLOAT DEFAULT 0;

COMMENT ON COLUMN mvp_topics.divergence_score IS 'Score representing the divergence of stances across countries (0.0 to 1.0)';
