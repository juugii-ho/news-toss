/**
 * Shared TypeScript types for News Spectrum
 */

export type StanceType = 'supportive' | 'factual' | 'critical';

export interface CountryStats {
  supportive: number;
  factual: number;
  critical: number;
}

export interface Topic {
  id: number;
  date: string;
  title: string;
  title_kr?: string | null;
  headline?: string | null;
  summary: string | null;
  thumbnail_url: string | null;
  divergence_score?: number;
  created_at?: string;
}

export interface Country {
  code: string;
  name: string;
  flag_emoji: string | null;
}

export interface Article {
  id: number;
  url: string;
  title: string;
  title_en?: string;
  title_kr?: string;
  source: string | null;
  country_code: string | null;
  published_at: string | null;
  stance: StanceType | null;
  topic_id: number | null;
  created_at: string;
  stance_score?: number;
  embedding?: number[] | string;
}

export interface TopicCountryStats {
  id: number;
  topic_id: number;
  country_code: string;
  supportive_count: number;
  factual_count: number;
  critical_count: number;
  summary: string | null;
  avg_score: number; // 0-100 stance score (0=critical, 50=neutral, 100=supportive)
  source_count?: number; // Number of unique news outlets covering this topic in this country
}

export interface TopicWithStats extends Topic {
  stats: TopicCountryStats[];
  countries_involved: string[];
  article_count: number;
  total_supportive: number;
  total_factual: number;
  total_critical: number;
  articles?: Article[];
}

export interface MegatopicCardProps {
  id: number;
  title: string;
  titleKr?: string | null;
  date: string;
  articleCount: number;
  countriesInvolved: string[];
  stats: Record<string, CountryStats>;
  summary?: string | null;
}

export interface SpectrumBarProps {
  supportive: number;
  factual: number;
  critical: number;
  minVisiblePercent?: number;
  showExplanation?: boolean;
  avgScore?: number; // 0-100 stance score
  height?: string; // Tailwind height class (e.g., "h-12")
}
