-- Add avg_score to mvp_topic_country_stats
-- Score range: 0 (Critical) to 100 (Supportive)
alter table public.mvp_topic_country_stats 
add column avg_score int default 50;
