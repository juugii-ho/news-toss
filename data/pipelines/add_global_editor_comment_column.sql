-- Add editor_comment column to mvp2_global_topics table
ALTER TABLE mvp2_global_topics
ADD COLUMN IF NOT EXISTS editor_comment TEXT;
