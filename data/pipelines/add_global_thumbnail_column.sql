-- Add thumbnail_url to mvp2_megatopics
ALTER TABLE mvp2_megatopics 
ADD COLUMN IF NOT EXISTS thumbnail_url TEXT;
