import { NextResponse } from "next/server";
import { supabase } from "@/lib/supabase-client";
import { readGlobalList } from "@/lib/mock";

export const revalidate = 0; // debugging, can set to 3600 for ISR

export async function GET() {
  if (!supabase) {
    const mock = await readGlobalList();
    return NextResponse.json(mock.items, { status: 200 });
  }

  try {
    const timeThreshold = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();

    const { data, error } = await supabase
      .from("mvp2_global_topics")
      .select("*")
      .gte("created_at", timeThreshold)
      .order("created_at", { ascending: false })
      .limit(50);

    if (error) throw error;

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
          .select("id, stances")
          .in("id", localTopicIds);

        if (localTopics) {
          // Map local topic ID to stances
          const localStanceMap = localTopics.reduce((acc: any, t: any) => {
            acc[t.id] = t.stances;
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

            childIds.forEach(childId => {
              const s = localStanceMap[childId] || {};
              if (s.factual) aggregated.factual.push(...(s.factual as string[]));
              if (s.critical) aggregated.critical.push(...(s.critical as string[]));
              if (s.supportive) aggregated.supportive.push(...(s.supportive as string[]));
            });
            stanceMap[globalId] = aggregated;
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
          thumbnail_url: topic.thumbnail_url || null,
          article_count: topic.article_count ?? 0,
          country_count,
          countries,
          created_at: topic.created_at,
          rank: topic.rank ?? null,
          is_pinned: topic.is_pinned ?? false,
          hero_image_url: null,
          hot_topic_badge: null,
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

    if (!mapped.length) {
      const mock = await readGlobalList();
      return NextResponse.json(mock.items, { status: 200 });
    }

    return NextResponse.json(mapped, { status: 200 });
  } catch (err) {
    console.error("GET /api/global/insights failed", err);
    const mock = await readGlobalList();
    return NextResponse.json(mock.items, { status: 200 });
  }
}
