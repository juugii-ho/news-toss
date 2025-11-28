/**
 * Database Types for News Spectrum MVP2
 * Auto-generated from Supabase schema
 * Created: 2025-11-28
 */

// ============================================================================
// Enums
// ============================================================================

export type PoliticalBias = 'CONSERVATIVE' | 'NEUTRAL' | 'PROGRESSIVE';
export type Stance = 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL';
export type ArticleStance = 'SUPPORTIVE' | 'NEUTRAL' | 'CRITICAL';
export type DisplayLevel = 1 | 2 | 3;
export type MediaType = 'image' | 'video';
export type TopicType = 'global' | 'local';
export type EntityType = 'article' | 'topic';

// ============================================================================
// Table Types
// ============================================================================

export interface Country {
  code: string; // VARCHAR(2) PRIMARY KEY
  name_en: string;
  name_ko: string;
  flag_emoji: string;
  created_at: string; // TIMESTAMPTZ
  updated_at: string; // TIMESTAMPTZ
}

export interface NewsSource {
  id: string; // UUID
  name: string;
  country_code: string; // FK to countries
  political_bias: PoliticalBias;
  rss_url: string;
  is_active: boolean;
  language: string; // VARCHAR(5)
  credibility_score?: number; // DECIMAL(3,2)
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface GlobalTopic {
  id: string; // UUID
  title_ko: string;
  title_en: string;
  intro_ko?: string;
  intro_en?: string;
  article_count: number;
  country_count: number;
  is_pinned: boolean;
  rank?: number;
  created_at: string;
  updated_at: string;
}

export interface Perspective {
  id: string; // UUID
  global_topic_id: string; // FK to global_topics
  country_code: string; // FK to countries
  stance: Stance;
  one_liner_ko: string;
  one_liner_en: string;
  source_link?: string;
  created_at: string;
  updated_at: string;
}

export interface LocalTopic {
  id: string; // UUID
  country_code: string; // FK to countries
  title: string;
  keyword?: string;
  article_count: number;
  display_level: DisplayLevel;
  media_type?: MediaType;
  media_url?: string;
  created_at: string;
  updated_at: string;
}

export interface Article {
  id: string; // UUID
  url: string; // UNIQUE
  title_original: string;
  title_ko?: string;
  title_en?: string;
  summary_original?: string;
  summary_ko?: string;
  summary_en?: string;
  country_code: string; // FK to countries
  source_id?: string; // FK to news_sources
  source_name: string;
  published_at: string; // TIMESTAMPTZ
  collected_at: string; // TIMESTAMPTZ
  global_topic_id?: string; // FK to global_topics
  local_topic_id?: string; // FK to local_topics
  created_at: string;
  updated_at: string;
}

export interface MediaAsset {
  id: string; // UUID
  topic_id: string;
  topic_type: TopicType;
  media_type: MediaType;
  url: string;
  width?: number;
  height?: number;
  duration?: number;
  prompt?: string;
  model_name?: string;
  created_at: string;
}

export interface ArticleStanceRecord {
  id: string; // UUID
  article_id: string; // FK to articles
  stance: ArticleStance;
  confidence_score: number; // DECIMAL(3,2)
  reasoning?: string;
  model_name: string;
  prompt_version?: string;
  created_at: string;
}

export interface Embedding {
  id: string; // UUID
  entity_type: EntityType;
  entity_id: string;
  embedding_vector: number[]; // vector(768)
  source_text_en: string;
  model_name: string;
  created_at: string;
}

export interface TopicRelation {
  id: string; // UUID
  parent_topic_id: string; // FK to global_topics
  child_topic_id: string; // FK to local_topics
  relevance_score?: number; // DECIMAL(3,2)
  created_at: string;
}

// ============================================================================
// Database Schema
// ============================================================================

export interface Database {
  public: {
    Tables: {
      MVP2_countries: {
        Row: Country;
        Insert: Omit<Country, 'created_at' | 'updated_at'>;
        Update: Partial<Omit<Country, 'code' | 'created_at' | 'updated_at'>>;
      };
      MVP2_news_sources: {
        Row: NewsSource;
        Insert: Omit<NewsSource, 'id' | 'created_at' | 'updated_at'>;
        Update: Partial<Omit<NewsSource, 'id' | 'created_at' | 'updated_at'>>;
      };
      MVP2_global_topics: {
        Row: GlobalTopic;
        Insert: Omit<GlobalTopic, 'id' | 'created_at' | 'updated_at'>;
        Update: Partial<Omit<GlobalTopic, 'id' | 'created_at' | 'updated_at'>>;
      };
      MVP2_perspectives: {
        Row: Perspective;
        Insert: Omit<Perspective, 'id' | 'created_at' | 'updated_at'>;
        Update: Partial<Omit<Perspective, 'id' | 'created_at' | 'updated_at'>>;
      };
      MVP2_local_topics: {
        Row: LocalTopic;
        Insert: Omit<LocalTopic, 'id' | 'created_at' | 'updated_at'>;
        Update: Partial<Omit<LocalTopic, 'id' | 'created_at' | 'updated_at'>>;
      };
      MVP2_articles: {
        Row: Article;
        Insert: Omit<Article, 'id' | 'created_at' | 'updated_at' | 'collected_at'>;
        Update: Partial<Omit<Article, 'id' | 'url' | 'created_at' | 'updated_at' | 'collected_at'>>;
      };
      MVP2_media_assets: {
        Row: MediaAsset;
        Insert: Omit<MediaAsset, 'id' | 'created_at'>;
        Update: Partial<Omit<MediaAsset, 'id' | 'created_at'>>;
      };
      MVP2_article_stance: {
        Row: ArticleStanceRecord;
        Insert: Omit<ArticleStanceRecord, 'id' | 'created_at'>;
        Update: Partial<Omit<ArticleStanceRecord, 'id' | 'article_id' | 'created_at'>>;
      };
      MVP2_embeddings: {
        Row: Embedding;
        Insert: Omit<Embedding, 'id' | 'created_at'>;
        Update: Partial<Omit<Embedding, 'id' | 'entity_type' | 'entity_id' | 'created_at'>>;
      };
      MVP2_topic_relations: {
        Row: TopicRelation;
        Insert: Omit<TopicRelation, 'id' | 'created_at'>;
        Update: Partial<Omit<TopicRelation, 'id' | 'parent_topic_id' | 'child_topic_id' | 'created_at'>>;
      };
    };
  };
}

// ============================================================================
// Helper Types
// ============================================================================

export type Tables<T extends keyof Database['public']['Tables']> = Database['public']['Tables'][T]['Row'];
export type Inserts<T extends keyof Database['public']['Tables']> = Database['public']['Tables'][T]['Insert'];
export type Updates<T extends keyof Database['public']['Tables']> = Database['public']['Tables'][T]['Update'];

// ============================================================================
// API Response Types
// ============================================================================

export interface GlobalInsightDetail {
  id: string;
  title_ko: string;
  title_en: string;
  intro_ko: string;
  intro_en: string;
  article_count: number;
  country_count: number;
  perspectives: {
    country_code: string;
    country_name_ko: string;
    country_name_en: string;
    flag_emoji: string;
    stance: Stance;
    one_liner_ko: string;
    one_liner_en: string;
    source_link?: string;
  }[];
}

export interface LocalTrendItem {
  topic_id: string;
  title: string;
  keyword?: string;
  article_count: number;
  display_level: DisplayLevel;
  media_type?: MediaType;
  media_url?: string;
}

export interface LocalTrendsResponse {
  country_code: string;
  country_name_ko: string;
  country_name_en: string;
  topics: LocalTrendItem[];
  page: number;
  total_count: number;
}
