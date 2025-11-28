-- Migration: Initial schema for News Spectrum MVP2
-- Created: 2025-11-28
-- Author: C (Claude Code)
-- Description: Creates 10 tables with indexes, constraints, and initial data
-- Note: MVP2_ prefix to coexist with existing MVP1 tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- 1. MVP2_countries (국가 마스터 테이블)
-- ============================================================================

CREATE TABLE IF NOT EXISTS MVP2_countries (
    code VARCHAR(2) PRIMARY KEY,
    name_en VARCHAR(100) NOT NULL,
    name_ko VARCHAR(100) NOT NULL,
    flag_emoji VARCHAR(10) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Insert country data
INSERT INTO MVP2_countries (code, name_en, name_ko, flag_emoji) VALUES
('US', 'United States', '미국', '🇺🇸'),
('GB', 'United Kingdom', '영국', '🇬🇧'),
('DE', 'Germany', '독일', '🇩🇪'),
('FR', 'France', '프랑스', '🇫🇷'),
('IT', 'Italy', '이탈리아', '🇮🇹'),
('JP', 'Japan', '일본', '🇯🇵'),
('KR', 'South Korea', '한국', '🇰🇷'),
('CA', 'Canada', '캐나다', '🇨🇦'),
('AU', 'Australia', '호주', '🇦🇺'),
('BE', 'Belgium', '벨기에', '🇧🇪'),
('NL', 'Netherlands', '네덜란드', '🇳🇱'),
('RU', 'Russia', '러시아', '🇷🇺'),
('CN', 'China', '중국', '🇨🇳');

-- ============================================================================
-- 2. MVP2_news_sources (언론사 마스터 테이블)
-- ============================================================================

CREATE TABLE IF NOT EXISTS MVP2_news_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    country_code VARCHAR(2) NOT NULL REFERENCES MVP2_countries(code) ON DELETE CASCADE,
    political_bias VARCHAR(15) NOT NULL CHECK (political_bias IN ('CONSERVATIVE', 'NEUTRAL', 'PROGRESSIVE')),
    rss_url TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    language VARCHAR(5) NOT NULL,
    credibility_score DECIMAL(3,2) CHECK (credibility_score >= 0 AND credibility_score <= 1),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_news_sources_country ON MVP2_news_sources(country_code);
CREATE INDEX IF NOT EXISTS idx_news_sources_active ON MVP2_news_sources(is_active);
CREATE INDEX IF NOT EXISTS idx_news_sources_bias ON MVP2_news_sources(political_bias);

-- Insert news sources (49 active + 2 inactive)
-- 🇺🇸 미국 (5개)
INSERT INTO MVP2_news_sources (name, country_code, political_bias, rss_url, language) VALUES
('New York Times', 'US', 'PROGRESSIVE', 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml', 'en'),
('Washington Post', 'US', 'PROGRESSIVE', 'https://feeds.washingtonpost.com/rss/national', 'en'),
('Fox News', 'US', 'CONSERVATIVE', 'https://moxie.foxnews.com/google-publisher/latest.xml', 'en'),
('CNN', 'US', 'NEUTRAL', 'http://rss.cnn.com/rss/edition.rss', 'en'),
('The Hill', 'US', 'NEUTRAL', 'https://thehill.com/feed/', 'en');

-- 🇬🇧 영국 (6개)
INSERT INTO MVP2_news_sources (name, country_code, political_bias, rss_url, language) VALUES
('BBC', 'GB', 'NEUTRAL', 'https://feeds.bbci.co.uk/news/rss.xml', 'en'),
('The Guardian', 'GB', 'PROGRESSIVE', 'https://www.theguardian.com/uk/rss', 'en'),
('Financial Times', 'GB', 'NEUTRAL', 'https://www.ft.com/rss/home', 'en'),
('The Independent', 'GB', 'PROGRESSIVE', 'https://www.independent.co.uk/news/uk/rss', 'en'),
('Sky News', 'GB', 'NEUTRAL', 'https://feeds.skynews.com/feeds/rss/home.xml', 'en'),
('The Telegraph', 'GB', 'CONSERVATIVE', 'https://www.telegraph.co.uk/news/rss.xml', 'en');

-- 🇩🇪 독일 (4개)
INSERT INTO MVP2_news_sources (name, country_code, political_bias, rss_url, language) VALUES
('Der Spiegel', 'DE', 'PROGRESSIVE', 'https://www.spiegel.de/schlagzeilen/index.rss', 'de'),
('FAZ', 'DE', 'CONSERVATIVE', 'https://www.faz.net/rss/aktuell/', 'de'),
('Süddeutsche Zeitung', 'DE', 'PROGRESSIVE', 'https://rss.sueddeutsche.de/rss/Topthemen', 'de'),
('Deutsche Welle', 'DE', 'NEUTRAL', 'https://rss.dw.com/rdf/rss-en-all', 'en');

-- 🇫🇷 프랑스 (4개)
INSERT INTO MVP2_news_sources (name, country_code, political_bias, rss_url, language) VALUES
('Le Monde', 'FR', 'PROGRESSIVE', 'http://www.lemonde.fr/rss/une.xml', 'fr'),
('Le Figaro', 'FR', 'CONSERVATIVE', 'https://www.lefigaro.fr/rss/figaro_flash-actu.xml', 'fr'),
('France 24', 'FR', 'NEUTRAL', 'https://www.france24.com/en/rss', 'en'),
('Mediapart', 'FR', 'PROGRESSIVE', 'https://www.mediapart.fr/articles/feed', 'fr');

-- 🇮🇹 이탈리아 (2개)
INSERT INTO MVP2_news_sources (name, country_code, political_bias, rss_url, language) VALUES
('La Repubblica', 'IT', 'PROGRESSIVE', 'https://www.repubblica.it/rss/homepage/rss2.0.xml', 'it'),
('Corriere della Sera', 'IT', 'CONSERVATIVE', 'https://www.corriere.it/rss/homepage.xml', 'it');

-- 🇯🇵 일본 (4개)
INSERT INTO MVP2_news_sources (name, country_code, political_bias, rss_url, language) VALUES
('Yomiuri Shimbun', 'JP', 'CONSERVATIVE', 'https://japannews.yomiuri.co.jp/feed', 'en'),
('Nikkei Asia', 'JP', 'NEUTRAL', 'https://asia.nikkei.com/rss/feed/nar', 'en'),
('NHK', 'JP', 'NEUTRAL', 'https://www3.nhk.or.jp/rss/news/cat0.xml', 'ja'),
('Asahi Shimbun', 'JP', 'PROGRESSIVE', 'https://www.asahi.com/rss/asahi/newsheadlines.rdf', 'ja');

-- 🇰🇷 한국 (5개)
INSERT INTO MVP2_news_sources (name, country_code, political_bias, rss_url, language) VALUES
('Google News Korea', 'KR', 'NEUTRAL', 'https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko', 'ko'),
('SBS', 'KR', 'NEUTRAL', 'https://news.sbs.co.kr/news/TopicRssFeed.do?plink=RSSREADER', 'ko'),
('조선일보', 'KR', 'CONSERVATIVE', 'https://www.chosun.com/arc/outboundfeeds/rss/?outputType=xml', 'ko'),
('동아일보', 'KR', 'CONSERVATIVE', 'https://rss.donga.com/total.xml', 'ko'),
('경향신문', 'KR', 'PROGRESSIVE', 'https://www.khan.co.kr/rss/rssdata/total_news.xml', 'ko');

-- 🇨🇦 캐나다 (4개 active + 1 inactive)
INSERT INTO MVP2_news_sources (name, country_code, political_bias, rss_url, language) VALUES
('National Post', 'CA', 'CONSERVATIVE', 'https://nationalpost.com/feed', 'en'),
('Globe and Mail - Business', 'CA', 'NEUTRAL', 'https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/business/', 'en'),
('Globe and Mail - Canada', 'CA', 'NEUTRAL', 'https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/canada/', 'en'),
('Globe and Mail - Politics', 'CA', 'NEUTRAL', 'https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/politics/', 'en');

INSERT INTO MVP2_news_sources (name, country_code, political_bias, rss_url, is_active, notes, language) VALUES
('CBC', 'CA', 'NEUTRAL', 'https://www.cbc.ca/cmlink/rss-topstories', false, 'Timeout issue - too slow', 'en');

-- 🇦🇺 호주 (3개)
INSERT INTO MVP2_news_sources (name, country_code, political_bias, rss_url, language) VALUES
('ABC Australia', 'AU', 'NEUTRAL', 'https://www.abc.net.au/news/feed/51120/rss.xml', 'en'),
('Sydney Morning Herald', 'AU', 'PROGRESSIVE', 'https://www.smh.com.au/rss/feed.xml', 'en'),
('The Age', 'AU', 'PROGRESSIVE', 'https://www.theage.com.au/rss/feed.xml', 'en');

-- 🇧🇪 벨기에 (2개 active + 1 inactive)
INSERT INTO MVP2_news_sources (name, country_code, political_bias, rss_url, language) VALUES
('La Libre', 'BE', 'NEUTRAL', 'https://www.lalibre.be/rss.xml', 'fr'),
('RTBF', 'BE', 'NEUTRAL', 'https://rss.rtbf.be/article/rss/highlight_rtbf_info.xml?source=internal', 'fr');

INSERT INTO MVP2_news_sources (name, country_code, political_bias, rss_url, is_active, notes, language) VALUES
('Le Soir', 'BE', 'PROGRESSIVE', 'https://www.lesoir.be/rss2/2/cible_principale', false, 'Access denied - blocked', 'fr');

-- 🇳🇱 네덜란드 (4개)
INSERT INTO MVP2_news_sources (name, country_code, political_bias, rss_url, language) VALUES
('NRC', 'NL', 'PROGRESSIVE', 'https://www.nrc.nl/rss/', 'nl'),
('De Telegraaf', 'NL', 'CONSERVATIVE', 'https://www.telegraaf.nl/rss', 'nl'),
('NOS', 'NL', 'NEUTRAL', 'https://feeds.nos.nl/nosnieuwsalgemeen', 'nl'),
('De Volkskrant', 'NL', 'PROGRESSIVE', 'https://www.volkskrant.nl/voorpagina/rss.xml', 'nl');

-- 🇷🇺 러시아 (4개)
INSERT INTO MVP2_news_sources (name, country_code, political_bias, rss_url, language) VALUES
('RT (Russia Today)', 'RU', 'CONSERVATIVE', 'https://www.rt.com/rss/news/', 'en'),
('TASS', 'RU', 'CONSERVATIVE', 'https://tass.com/rss/v2.xml', 'en'),
('Kommersant', 'RU', 'NEUTRAL', 'https://www.kommersant.ru/RSS/news.xml', 'ru'),
('Novaya Gazeta', 'RU', 'PROGRESSIVE', 'https://novayagazeta.eu/feed/rss/en', 'en');

-- 🇨🇳 중국 (2개)
INSERT INTO MVP2_news_sources (name, country_code, political_bias, rss_url, language) VALUES
('Xinhua', 'CN', 'CONSERVATIVE', 'http://www.xinhuanet.com/english/rss/chinarss.xml', 'en'),
('South China Morning Post', 'CN', 'NEUTRAL', 'https://www.scmp.com/rss/91/feed', 'en');

-- ============================================================================
-- 3. MVP2_global_topics (글로벌 인사이트 토픽)
-- ============================================================================

CREATE TABLE IF NOT EXISTS MVP2_global_topics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title_ko VARCHAR(200) NOT NULL,
    title_en VARCHAR(200) NOT NULL,
    intro_ko TEXT,
    intro_en TEXT,
    article_count INTEGER NOT NULL DEFAULT 0,
    country_count INTEGER NOT NULL DEFAULT 0,
    is_pinned BOOLEAN NOT NULL DEFAULT false,
    rank INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_global_topics_rank ON MVP2_global_topics(rank) WHERE rank IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_global_topics_pinned ON MVP2_global_topics(is_pinned);
CREATE INDEX IF NOT EXISTS idx_global_topics_created ON MVP2_global_topics(created_at DESC);

-- ============================================================================
-- 4. MVP2_perspectives (국가별 관점 - VS 카드)
-- ============================================================================

CREATE TABLE IF NOT EXISTS MVP2_perspectives (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    global_topic_id UUID NOT NULL REFERENCES MVP2_global_topics(id) ON DELETE CASCADE,
    country_code VARCHAR(2) NOT NULL REFERENCES MVP2_countries(code) ON DELETE CASCADE,
    stance VARCHAR(10) NOT NULL CHECK (stance IN ('POSITIVE', 'NEGATIVE', 'NEUTRAL')),
    one_liner_ko TEXT NOT NULL,
    one_liner_en TEXT NOT NULL,
    source_link TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(global_topic_id, country_code)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_perspectives_topic ON MVP2_perspectives(global_topic_id);
CREATE INDEX IF NOT EXISTS idx_perspectives_country ON MVP2_perspectives(country_code);
CREATE INDEX IF NOT EXISTS idx_perspectives_stance ON MVP2_perspectives(stance);

-- ============================================================================
-- 5. MVP2_local_topics (국가별 트렌드 토픽)
-- ============================================================================

CREATE TABLE IF NOT EXISTS MVP2_local_topics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    country_code VARCHAR(2) NOT NULL REFERENCES MVP2_countries(code) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    keyword VARCHAR(50),
    article_count INTEGER NOT NULL DEFAULT 0,
    display_level INTEGER NOT NULL CHECK (display_level IN (1, 2, 3)),
    media_type VARCHAR(10) CHECK (media_type IN ('image', 'video')),
    media_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_local_topics_country ON MVP2_local_topics(country_code);
CREATE INDEX IF NOT EXISTS idx_local_topics_count ON MVP2_local_topics(article_count DESC);
CREATE INDEX IF NOT EXISTS idx_local_topics_level ON MVP2_local_topics(display_level);
CREATE INDEX IF NOT EXISTS idx_local_topics_created ON MVP2_local_topics(created_at DESC);

-- ============================================================================
-- 6. MVP2_articles (원본 기사)
-- ============================================================================

CREATE TABLE IF NOT EXISTS MVP2_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url TEXT NOT NULL UNIQUE,
    title_original TEXT NOT NULL,
    title_ko TEXT,
    title_en TEXT,
    summary_original TEXT,
    summary_ko TEXT,
    summary_en TEXT,
    country_code VARCHAR(2) NOT NULL REFERENCES MVP2_countries(code) ON DELETE CASCADE,
    source_id UUID REFERENCES MVP2_news_sources(id) ON DELETE SET NULL,
    source_name VARCHAR(100) NOT NULL,
    published_at TIMESTAMPTZ NOT NULL,
    collected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    global_topic_id UUID REFERENCES MVP2_global_topics(id) ON DELETE SET NULL,
    local_topic_id UUID REFERENCES MVP2_local_topics(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_articles_url ON MVP2_articles(url);
CREATE INDEX IF NOT EXISTS idx_articles_country ON MVP2_articles(country_code);
CREATE INDEX IF NOT EXISTS idx_articles_source ON MVP2_articles(source_id);
CREATE INDEX IF NOT EXISTS idx_articles_published ON MVP2_articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_global_topic ON MVP2_articles(global_topic_id);
CREATE INDEX IF NOT EXISTS idx_articles_local_topic ON MVP2_articles(local_topic_id);

-- ============================================================================
-- 7. MVP2_media_assets (AI 생성 미디어)
-- ============================================================================

CREATE TABLE IF NOT EXISTS MVP2_media_assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic_id UUID NOT NULL,
    topic_type VARCHAR(10) NOT NULL CHECK (topic_type IN ('global', 'local')),
    media_type VARCHAR(10) NOT NULL CHECK (media_type IN ('image', 'video')),
    url TEXT NOT NULL,
    width INTEGER,
    height INTEGER,
    duration INTEGER,
    prompt TEXT,
    model_name VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_media_topic ON MVP2_media_assets(topic_id, topic_type);
CREATE INDEX IF NOT EXISTS idx_media_type ON MVP2_media_assets(media_type);

-- ============================================================================
-- 8. MVP2_article_stance (LLM 스탠스 분석)
-- ============================================================================

CREATE TABLE IF NOT EXISTS MVP2_article_stance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    article_id UUID NOT NULL REFERENCES MVP2_articles(id) ON DELETE CASCADE,
    stance VARCHAR(15) NOT NULL CHECK (stance IN ('SUPPORTIVE', 'NEUTRAL', 'CRITICAL')),
    confidence_score DECIMAL(3,2) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    reasoning TEXT,
    model_name VARCHAR(50) NOT NULL,
    prompt_version VARCHAR(20),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(article_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_article_stance_article ON MVP2_article_stance(article_id);
CREATE INDEX IF NOT EXISTS idx_article_stance_stance ON MVP2_article_stance(stance);

-- ============================================================================
-- 9. MVP2_embeddings (임베딩 벡터)
-- ============================================================================

CREATE TABLE IF NOT EXISTS MVP2_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(10) NOT NULL CHECK (entity_type IN ('article', 'topic')),
    entity_id UUID NOT NULL,
    embedding_vector vector(768) NOT NULL,
    source_text_en TEXT NOT NULL,
    model_name VARCHAR(50) NOT NULL DEFAULT 'text-embedding-004',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(entity_type, entity_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_embeddings_entity ON MVP2_embeddings(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON MVP2_embeddings USING hnsw (embedding_vector vector_cosine_ops);

-- ============================================================================
-- 10. MVP2_topic_relations (토픽 계층 관계)
-- ============================================================================

CREATE TABLE IF NOT EXISTS MVP2_topic_relations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parent_topic_id UUID NOT NULL REFERENCES MVP2_global_topics(id) ON DELETE CASCADE,
    child_topic_id UUID NOT NULL REFERENCES MVP2_local_topics(id) ON DELETE CASCADE,
    relevance_score DECIMAL(3,2) CHECK (relevance_score >= 0 AND relevance_score <= 1),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(parent_topic_id, child_topic_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_topic_relations_parent ON MVP2_topic_relations(parent_topic_id);
CREATE INDEX IF NOT EXISTS idx_topic_relations_child ON MVP2_topic_relations(child_topic_id);

-- ============================================================================
-- Triggers for updated_at
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE OR REPLACE TRIGGER update_countries_updated_at BEFORE UPDATE ON MVP2_countries FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE OR REPLACE TRIGGER update_news_sources_updated_at BEFORE UPDATE ON MVP2_news_sources FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE OR REPLACE TRIGGER update_global_topics_updated_at BEFORE UPDATE ON MVP2_global_topics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE OR REPLACE TRIGGER update_perspectives_updated_at BEFORE UPDATE ON MVP2_perspectives FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE OR REPLACE TRIGGER update_local_topics_updated_at BEFORE UPDATE ON MVP2_local_topics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE OR REPLACE TRIGGER update_articles_updated_at BEFORE UPDATE ON MVP2_articles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Comments
-- ============================================================================

COMMENT ON TABLE MVP2_countries IS '국가 마스터 테이블 (13개국)';
COMMENT ON TABLE MVP2_news_sources IS '언론사 마스터 테이블 (49개 active + 2개 inactive)';
COMMENT ON TABLE MVP2_global_topics IS '글로벌 인사이트 토픽 (Top 10)';
COMMENT ON TABLE MVP2_perspectives IS '국가별 관점 - VS 카드';
COMMENT ON TABLE MVP2_local_topics IS '국가별 트렌드 토픽 - Mosaic';
COMMENT ON TABLE MVP2_articles IS '원본 기사 데이터';
COMMENT ON TABLE MVP2_media_assets IS 'AI 생성 미디어 (이미지/비디오)';
COMMENT ON TABLE MVP2_article_stance IS 'LLM 스탠스 분석 결과';
COMMENT ON TABLE MVP2_embeddings IS '임베딩 벡터 (시각화용)';
COMMENT ON TABLE MVP2_topic_relations IS '토픽 계층 관계 (Local → Global)';
