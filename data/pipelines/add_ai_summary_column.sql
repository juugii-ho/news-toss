-- Add ai_summary column to mvp2_topics table
ALTER TABLE mvp2_topics ADD COLUMN IF NOT EXISTS ai_summary TEXT;
