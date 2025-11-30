SELECT 
    name, 
    country_count, 
    article_count, 
    countries, 
    created_at 
FROM mvp2_megatopics 
ORDER BY created_at DESC, country_count DESC 
LIMIT 20;
