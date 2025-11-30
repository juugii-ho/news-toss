-- Add category, keywords, and stances columns to mvp2_global_topics
ALTER TABLE mvp2_global_topics 
ADD COLUMN IF NOT EXISTS category TEXT,
ADD COLUMN IF NOT EXISTS keywords TEXT[],
ADD COLUMN IF NOT EXISTS stances JSONB;

-- Update comment
COMMENT ON COLUMN mvp2_global_topics.category IS 'Topic category (Politics, Economy, Society, Tech, World, Culture, Sports, Entertainment)';
COMMENT ON COLUMN mvp2_global_topics.keywords IS 'Array of keywords for the topic';
COMMENT ON COLUMN mvp2_global_topics.stances IS 'JSONB array of stance objects with country perspectives';
