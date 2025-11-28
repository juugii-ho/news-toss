-- Create mvp_topic_history table
CREATE TABLE IF NOT EXISTS mvp_topic_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic_id BIGINT REFERENCES mvp_topics(id), -- Changed to BIGINT to match mvp_topics.id
    date DATE NOT NULL,
    title_en TEXT,
    title_kr TEXT,
    centroid_embedding VECTOR(768),
    article_count INT,
    country_count INT,
    avg_stance_score FLOAT,
    drift_score FLOAT, -- Cosine distance from previous day's topic
    is_new_topic BOOLEAN DEFAULT false,
    parent_topic_id UUID REFERENCES mvp_topic_history(id), -- Link to yesterday's history record
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_topic_history_date ON mvp_topic_history(date);
CREATE INDEX IF NOT EXISTS idx_topic_history_topic_id ON mvp_topic_history(topic_id);
