/**
 * Shared constants for News Spectrum
 */

export const COUNTRY_FLAGS: Record<string, string> = {
  US: "🇺🇸",
  GB: "🇬🇧",
  FR: "🇫🇷",
  DE: "🇩🇪",
  KR: "🇰🇷",
  CN: "🇨🇳",
  RU: "🇷🇺",
  JP: "🇯🇵",
  CA: "🇨🇦",
  IT: "🇮🇹",
  IN: "🇮🇳",
  BR: "🇧🇷",
  AU: "🇦🇺",
  UA: "🇺🇦",
  IL: "🇮🇱",
  PS: "🇵🇸",
} as const;

export const COUNTRY_NAMES: Record<string, string> = {
  US: "United States",
  GB: "United Kingdom",
  FR: "France",
  DE: "Germany",
  KR: "South Korea",
  CN: "China",
  RU: "Russia",
  JP: "Japan",
  CA: "Canada",
  IT: "Italy",
  IN: "India",
  BR: "Brazil",
  AU: "Australia",
  UA: "Ukraine",
  IL: "Israel",
  PS: "Palestine",
} as const;

export const STANCE_TYPES = {
  SUPPORTIVE: "supportive",
  FACTUAL: "factual",
  CRITICAL: "critical",
} as const;

export const STANCE_EXPLANATIONS = {
  supportive: "Articles with a generally favorable or aligned tone toward the topic",
  factual: "Articles presenting information with a neutral, objective tone",
  critical: "Articles expressing concerns, opposition, or critical perspective",
} as const;

export const CONTENT_LABELS = {
  AI_SUMMARY: "AI-generated summary",
  AI_ANALYSIS: "AI-analyzed content",
  SOURCES: "Sources",
} as const;

export const APP_CONFIG = {
  name: "News Spectrum",
  tagline: "Global Intelligence Platform",
  description: "Understand global issues not as a single headline, but as a spectrum of perspectives across countries, blocs, and media outlets.",
  pipelineSchedule: "23:30 KST",
} as const;

/**
 * Get the default thumbnail URL from Supabase Storage
 * Falls back to placeholder path if Supabase is not configured
 */
export const getDefaultThumbnailUrl = (): string => {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  if (supabaseUrl) {
    return `${supabaseUrl}/storage/v1/object/public/thumbnails/placeholders/default.jpg`;
  }
  // Fallback for local development or when Supabase is not configured
  return '/placeholders/default.jpg';
};

/**
 * Get country flag emoji with fallback
 */
export const getCountryFlag = (countryCode: string): string => {
  return COUNTRY_FLAGS[countryCode] || '🏳️';
};

/**
 * Get country name with fallback to country code
 */
export const getCountryName = (countryCode: string): string => {
  return COUNTRY_NAMES[countryCode] || countryCode;
};
