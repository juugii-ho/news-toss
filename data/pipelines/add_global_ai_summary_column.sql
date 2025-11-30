-- Add ai_summary column to mvp2_global_topics table
ALTER TABLE mvp2_global_topics
ADD COLUMN IF NOT EXISTS ai_summary TEXT;
