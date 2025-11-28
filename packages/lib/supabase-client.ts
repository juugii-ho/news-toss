import { createClient } from "supabase-js";
import type { Database } from "./database-types";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn("[supabase] NEXT_PUBLIC_SUPABASE_URL or ANON_KEY is not set. API routes will fallback to mock data.");
}

export const supabase = supabaseUrl && supabaseAnonKey
  ? createClient<Database>(supabaseUrl, supabaseAnonKey)
  : null;
