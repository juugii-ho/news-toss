import { supabase } from "./supabase-client";
import { GlobalListResponse, LocalListResponse, GlobalItem, LocalItem } from "./mock";

export const SupabaseNewsService = {
    async getMegatopics(): Promise<GlobalListResponse> {
        if (!supabase) {
            console.warn("Supabase client not initialized");
            return { items: [] };
        }
        try {
            // Calculate 24 hours ago
            const timeThreshold = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();

            const { data, error } = await supabase
                .from("mvp2_megatopics")
                .select("*")
                .gte("created_at", timeThreshold) // Filter for freshness
                .order("article_count", { ascending: false })
                .limit(50); // Fetch more to allow client-side sorting/filtering

            if (error) throw error;

            let rows = data || [];

            if (!rows.length) {
                const { data: latest, error: latestError } = await supabase
                    .from("mvp2_megatopics")
                    .select("*")
                    .order("created_at", { ascending: false })
                    .order("article_count", { ascending: false })
                    .limit(50);
                if (latestError) throw latestError;
                rows = latest || [];
            }

            // Map DB rows to GlobalItem
            const items: GlobalItem[] = rows.map((row: any) => ({
                id: row.id,
                rank: 0, // Will be assigned after sort
                is_pinned: row.is_pinned ?? false,
                title_ko: row.title_ko ?? row.headline ?? row.topic_name ?? "",
                category: "Global",
                hero_image_url: undefined, // TODO: Add image support
                country_count: row.country_count ?? 0,
                hot_topic_badge: row.article_count > 50 ? "Hot" : null,
                keywords: row.keywords || [],
                thumbnail_url: undefined,
                countries: row.keywords || []
            }));

            // Sort by Country Count (Desc) -> Total Articles (Desc)
            items.sort((a, b) => {
                const countA = a.country_count || 0;
                const countB = b.country_count || 0;
                if (countB !== countA) {
                    return countB - countA;
                }
                const artA = (a as any).article_count || 0;
                const artB = (b as any).article_count || 0;
                return artB - artA;
            });

            // Re-assign ranks
            items.forEach((item, idx) => {
                item.rank = idx + 1;
            });

            return { items };
        } catch (err) {
            console.error("Error fetching megatopics:", err);
            return { items: [] };
        }
    },

    async getTopics(countryCode: string = "KR"): Promise<LocalListResponse> {
        if (!supabase) {
            console.warn("Supabase client not initialized");
            return {
                country: countryCode,
                page: 1,
                items: [],
                hasNextPage: false
            };
        }
        try {
            // Calculate 24 hours ago
            const timeThreshold = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();

            const { data, error } = await supabase
                .from("mvp2_topics")
                .select("*")
                .eq("country_code", countryCode)
                .gte("created_at", timeThreshold) // Filter for freshness
                .gt("source_count", 1) // Strict Filter: Must have at least 2 sources
                .order("source_count", { ascending: false })
                .order("article_count", { ascending: false })
                .limit(20);

            if (error) throw error;

            // Map DB rows to LocalItem
            const items: LocalItem[] = (data || []).map((row: any) => ({
                topic_id: row.id,
                title: row.headline || row.topic_name, // Use headline if available, else topic_name
                keyword: (row.keywords && row.keywords.length > 0) ? row.keywords[0] : row.topic_name, // Use first keyword or fallback to topic name
                article_count: row.article_count,
                display_level: row.article_count > 10 ? 1 : 2, // Simple logic
                media_type: "NONE",
                media_url: undefined
            }));

            return {
                country: countryCode,
                page: 1,
                items,
                hasNextPage: false
            };
        } catch (err) {
            console.error(`Error fetching topics for ${countryCode}:`, err);
            return {
                country: countryCode,
                page: 1,
                items: [],
                hasNextPage: false
            };
        }
    }
};
