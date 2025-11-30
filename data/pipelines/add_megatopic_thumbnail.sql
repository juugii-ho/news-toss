-- Add thumbnail_url to mvp2_megatopics
ALTER TABLE mvp2_megatopics 
ADD COLUMN IF NOT EXISTS thumbnail_url TEXT,
ADD COLUMN IF NOT EXISTS editor_comment TEXT,
ADD COLUMN IF NOT EXISTS ai_summary TEXT;
