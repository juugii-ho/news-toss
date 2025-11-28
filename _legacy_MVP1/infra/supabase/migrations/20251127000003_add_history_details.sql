-- Add rich metadata columns to mvp_topic_history for "News Weather Map" visualization
ALTER TABLE mvp_topic_history
ADD COLUMN IF NOT EXISTS intensity INT,           -- article_count * country_count (Impact Score)
ADD COLUMN IF NOT EXISTS category INT,            -- 1-5 (Storm Category / Size Class)
ADD COLUMN IF NOT EXISTS status VARCHAR(20),      -- forming, strengthening, mature, weakening, dissipating
ADD COLUMN IF NOT EXISTS countries TEXT[];        -- Array of country codes involved
