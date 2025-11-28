import { createClient, SupabaseClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

// Lazy initialization - only create client when actually used
let supabaseClient: SupabaseClient | null = null;

export function getSupabaseClient(): SupabaseClient {
  if (!supabaseUrl || !supabaseAnonKey) {
    throw new Error(
      'Missing Supabase environment variables. Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in .env.local'
    );
  }

  if (!supabaseClient) {
    supabaseClient = createClient(supabaseUrl, supabaseAnonKey);
  }

  return supabaseClient;
}

// Helper to check if Supabase is configured
export function isSupabaseConfigured(): boolean {
  return !!(supabaseUrl && supabaseAnonKey);
}

// For backwards compatibility (deprecated)
export const supabase = new Proxy({} as SupabaseClient, {
  get: (_target, prop) => {
    console.warn('Direct supabase import is deprecated. Use getSupabaseClient() instead.');
    return getSupabaseClient()[prop as keyof SupabaseClient];
  }
});

// Re-export types from centralized types file
export type {
  Topic,
  Country,
  Article,
  TopicCountryStats,
  TopicWithStats,
  StanceType,
} from './types';
