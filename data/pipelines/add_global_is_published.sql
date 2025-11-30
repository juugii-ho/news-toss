-- Add is_published and batch_id to mvp2_global_topics
ALTER TABLE mvp2_global_topics 
ADD COLUMN IF NOT EXISTS is_published BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS batch_id UUID;

-- Create index for faster filtering
CREATE INDEX IF NOT EXISTS idx_mvp2_global_topics_is_published ON mvp2_global_topics(is_published);
CREATE INDEX IF NOT EXISTS idx_mvp2_global_topics_batch_id ON mvp2_global_topics(batch_id);

-- Update existing records to be published (for now, to fix immediate issue)
-- Or we can let the python script handle it. 
-- Let's set them to TRUE if they match the latest batch from megatopics?
-- Actually, better to run the python script again.
