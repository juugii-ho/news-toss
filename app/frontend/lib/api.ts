import { supabase } from "./supabase-client";
import { readGlobalList, readLocalList, readVsCard } from "./mock";
import type { GlobalItem, GlobalListResponse, VsCard, LocalListResponse, LocalItem } from "./mock";

const REVALIDATE_SECONDS = 0;

async function fetchJson<T>(url: string): Promise<T> {
  const absoluteUrl =
    url.startsWith("http") || url.startsWith("https")
      ? url
      : process.env.VERCEL_URL
        ? `https://${process.env.VERCEL_URL}${url}`
        : `${process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000"}${url}`;
  const res = await fetch(absoluteUrl, { next: { revalidate: REVALIDATE_SECONDS } });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed fetch: ${url} (${res.status}) - ${text}`);
  }
  return (await res.json()) as T;
}

export async function getGlobalList(): Promise<GlobalListResponse> {
  // If no Supabase client (e.g. build time without env vars), return mock
  if (!supabase) {
    return readGlobalList();
  }

  try {
    // Relax time filter to 7 days to avoid timezone issues
    const timeThreshold = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();

    const { data, error } = await supabase
      .from("mvp2_megatopics")
      .select("*")
      .gte("created_at", timeThreshold)
      .eq("is_published", true)
      .order("created_at", { ascending: false })
      .limit(50);

    if (error) throw error;

    if (!data || data.length === 0) {
      return { items: [] };
    }

    const megatopics = (data || []).map((m: any) => ({
      ...m,
      created_at: m.created_at || m.createdAt || m.createdAtUtc || null
    }));
    const ids = megatopics.map((m: any) => m.id).filter(Boolean);

    // gather countries and stances from articles/topics
    let countryMap: Record<string, string[]> = {};
    let stanceMap: Record<string, any> = {};

    if (ids.length) {
      // Fetch articles to get countries AND link to local topics
      const { data: articles } = await supabase
        .from("mvp2_articles")
        .select("global_topic_id, country_code, local_topic_id")
        .in("global_topic_id", ids);

      let localTopicIds: string[] = [];
      let globalToLocalMap: Record<string, Set<string>> = {};

      if (articles) {
        countryMap = articles.reduce((acc: any, row: any) => {
          if (!row.global_topic_id) return acc;
          const key = row.global_topic_id;
          acc[key] = acc[key] || [];
          if (row.country_code && !acc[key].includes(row.country_code)) {
            acc[key].push(row.country_code);
          }

          // Collect local topic IDs
          if (row.local_topic_id) {
            localTopicIds.push(row.local_topic_id);
            if (!globalToLocalMap[key]) globalToLocalMap[key] = new Set();
            globalToLocalMap[key].add(row.local_topic_id);
          }
          return acc;
        }, {});
      }

      // Fetch stances from child local topics
      if (localTopicIds.length > 0) {
        const { data: localTopics } = await supabase
          .from("mvp2_topics")
          .select("id, stances, thumbnail_url")
          .in("id", localTopicIds);

        if (localTopics) {
          // Map local topic ID to stances AND thumbnails
          const localDataMap = localTopics.reduce((acc: any, t: any) => {
            acc[t.id] = { stances: t.stances, thumbnail: t.thumbnail_url };
            return acc;
          }, {});

          // Aggregate back to global topics
          Object.keys(globalToLocalMap).forEach(globalId => {
            const childIds = Array.from(globalToLocalMap[globalId]);
            const aggregated: { factual: string[], critical: string[], supportive: string[] } = {
              factual: [],
              critical: [],
              supportive: []
            };
            let thumb: string | null = null;

            childIds.forEach(childId => {
              const d = localDataMap[childId] || {};
              const s = d.stances || {};
              if (s.factual) aggregated.factual.push(...(s.factual as string[]));
              if (s.critical) aggregated.critical.push(...(s.critical as string[]));
              if (s.supportive) aggregated.supportive.push(...(s.supportive as string[]));

              // Pick first available thumbnail
              if (!thumb && d.thumbnail) thumb = d.thumbnail;
            });
            stanceMap[globalId] = aggregated;
            // Hack: Store thumbnail in stanceMap temporarily
            (stanceMap[globalId] as any)._thumbnail = thumb;
          });
        }
      }
    }

    const mapped =
      megatopics.map((topic: any) => {
        const mergedCountries = new Set<string>();
        (countryMap[topic.id] || []).forEach((c) => c && mergedCountries.add(c));
        (topic.countries || []).forEach((c: string) => c && mergedCountries.add(c));
        const countries = Array.from(mergedCountries);
        const country_count =
          countries.length > 0 ? countries.length : topic.country_count ?? 0;
        const aggregatedStances = stanceMap[topic.id] || topic.stances || [];
        let formattedStances: any[] = [];
        if (aggregatedStances.factual || aggregatedStances.critical || aggregatedStances.supportive) {
          const s = aggregatedStances;
          (s.factual || []).forEach(() => formattedStances.push({ stance: "NEUTRAL" }));
          (s.critical || []).forEach(() => formattedStances.push({ stance: "NEGATIVE" }));
          (s.supportive || []).forEach(() => formattedStances.push({ stance: "POSITIVE" }));
        } else if (Array.isArray(aggregatedStances)) {
          formattedStances = aggregatedStances;
        }

        return {
          id: topic.id,
          title_ko: topic.headline ?? topic.title_ko ?? topic.name ?? "",
          title_en: topic.title_en ?? "",
          intro_ko: topic.intro_ko ?? "",
          intro_en: topic.intro_en ?? "",
          thumbnail_url: topic.thumbnail_url || (stanceMap[topic.id] as any)?._thumbnail || null,
          article_count: topic.article_count ?? 0,
          country_count,
          countries,
          created_at: topic.created_at,
          rank: topic.rank ?? undefined,
          is_pinned: topic.is_pinned ?? false,
          hero_image_url: undefined,
          hot_topic_badge: undefined,
          stances: formattedStances,
          x: topic.x,
          y: topic.y
        };
      });

    mapped.sort((a: any, b: any) => {
      // 랭크가 있으면 우선
      if (a.rank != null && b.rank != null && a.rank !== b.rank) {
        return a.rank - b.rank;
      }
      const cA = a.country_count ?? 0;
      const cB = b.country_count ?? 0;
      if (cB !== cA) return cB - cA;
      const aA = a.article_count ?? 0;
      const aB = b.article_count ?? 0;
      if (aB !== aA) return aB - aA;
      return new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime();
    });

    return { items: mapped };
  } catch (err) {
    console.warn("API Error (getGlobalList):", err);
    return readGlobalList();
  }
}

export async function getVsCard(id = "global_001"): Promise<VsCard> {
  try {
    return await fetchJson<VsCard>(`/api/global/insights/${id}`);
  } catch (err) {
    console.warn("Falling back to mock VS card:", err);
    return readVsCard();
  }
}

export async function getLocalList(params?: { country?: string; page?: number }): Promise<LocalListResponse> {
  const country = params?.country ?? "KR";
  const page = params?.page ?? 1;
  const query = new URLSearchParams({ country, page: String(page) }).toString();
  try {
    const data = await fetchJson<any>(`/api/local/trends?${query}`);
    // API spec returns topics[]; map to items[] shape for UI compatibility
    if (data?.topics) {
      return {
        country: data.country_code ?? country,
        page: data.page ?? page,
        items: data.topics.map((t: any) => ({
          topic_id: t.topic_id ?? t.id,
          title: t.title,
          keyword: t.keyword,
          article_count: t.article_count,
          display_level: t.display_level,
          ai_summary: t.ai_summary,
          media_type:
            (t.media_type as any) === "IMAGE"
              ? "IMAGE"
              : (t.media_type as any) === "VIDEO"
                ? "VIDEO"
                : t.media_type === "NONE"
                  ? "NONE"
                  : "NONE",
          media_url: t.media_url,
          is_global: Boolean(t.is_global)
        })),
        hasNextPage: Boolean(
          data.total_count
            ? (data.page ?? 1) * (data.limit ?? data.topics.length ?? 20) < data.total_count
            : data.hasNextPage ?? false
        )
      };
    }
    return data as LocalListResponse;
  } catch (err) {
    console.warn("Falling back to mock local list:", err);
    return readLocalList();
  }
}

export async function getLocalTopic(id: string): Promise<LocalItem> {
  try {
    return await fetchJson<LocalItem>(`/api/local/topics/${id}`);
  } catch (err) {
    console.warn("Falling back to mock local topic:", err);
    const mock = await readLocalList();
    const found = mock.items.find((i) => i.topic_id === id);
    if (found) return found;
    throw err;
  }
}
