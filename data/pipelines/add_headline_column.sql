-- Add headline column to mvp2_topics
ALTER TABLE mvp2_topics ADD COLUMN IF NOT EXISTS headline TEXT;

-- Add headline column to mvp2_megatopics
ALTER TABLE mvp2_megatopics ADD COLUMN IF NOT EXISTS headline TEXT;
