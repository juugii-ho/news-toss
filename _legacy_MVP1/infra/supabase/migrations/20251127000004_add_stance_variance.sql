-- Add stance_variance column to mvp_topic_history for visualization color mapping
ALTER TABLE mvp_topic_history
ADD COLUMN IF NOT EXISTS stance_variance FLOAT; -- Variance of stance scores (0-100)
