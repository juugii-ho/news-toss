-- Add is_published column to mvp2_topics and mvp2_megatopics
-- This allows atomic updates: prepare data in background, then publish all at once

-- Add to mvp2_topics
ALTER TABLE mvp2_topics 
ADD COLUMN IF NOT EXISTS is_published BOOLEAN DEFAULT FALSE;

-- Add to mvp2_megatopics
ALTER TABLE mvp2_megatopics 
ADD COLUMN IF NOT EXISTS is_published BOOLEAN DEFAULT FALSE;

-- Add batch_id for tracking pipeline runs
ALTER TABLE mvp2_topics 
ADD COLUMN IF NOT EXISTS batch_id UUID;

ALTER TABLE mvp2_megatopics 
ADD COLUMN IF NOT EXISTS batch_id UUID;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_topics_published ON mvp2_topics(is_published) WHERE is_published = TRUE;
CREATE INDEX IF NOT EXISTS idx_megatopics_published ON mvp2_megatopics(is_published) WHERE is_published = TRUE;
CREATE INDEX IF NOT EXISTS idx_topics_batch ON mvp2_topics(batch_id);
CREATE INDEX IF NOT EXISTS idx_megatopics_batch ON mvp2_megatopics(batch_id);

-- Set existing data as published (for backward compatibility)
UPDATE mvp2_topics SET is_published = TRUE WHERE is_published IS NULL;
UPDATE mvp2_megatopics SET is_published = TRUE WHERE is_published IS NULL;
