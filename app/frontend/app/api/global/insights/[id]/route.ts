import { NextResponse } from "next/server";
import { supabase } from "@/lib/supabase-client";
import { readVsCard } from "@/lib/mock";

export const dynamic = 'force-dynamic';
export const revalidate = 0;

type Params = {
  params: { id: string };
};

function getFlagEmoji(countryCode: string) {
  const codePoints = countryCode
    .toUpperCase()
    .split("")
    .map((char) => 127397 + char.charCodeAt(0));
  return String.fromCodePoint(...codePoints);
}

export async function GET(_req: Request, { params }: Params) {
  const id = params.id;

  if (!supabase) {
    const mock = await readVsCard();
    return NextResponse.json(mock, { status: 200 });
  }

  try {
    const fetchLatest = async () => {
      const { data, error } = await supabase!
        .from("mvp2_megatopics")
        .select("*")
        .order("created_at", { ascending: false })
        .order("rank", { ascending: true })
        .limit(1)
        .maybeSingle();
      if (error) throw error;
      return data;
    };

    const tryId = async () => {
      const { data, error } = await supabase!
        .from("mvp2_megatopics")
        .select("*")
        .eq("id", id)
        .maybeSingle();
      if (error) throw error;
      return data;
    };

    let data: any | null = null;
    try {
      data = await tryId();
    } catch (err: any) {
      if (err?.code === "22P02" || err?.message?.includes("invalid input syntax")) {
        data = await fetchLatest();
      } else {
        throw err;
      }
    }

    // If not found, fallback to latest instead of 404 to avoid mock 표시
    if (!data) {
      data = await fetchLatest();
    }

    if (!data) {
      const mock = await readVsCard();
      return NextResponse.json(mock, { status: 200 });
    }

    // 1. Fetch child Local Topics indirectly via articles
    // First, get local_topic_ids from articles linked to this global topic
    const { data: linkedArticles } = await supabase!
      .from("mvp2_articles")
      .select("local_topic_id")
      .eq("global_topic_id", data.id)
      .not("local_topic_id", "is", null);

    let localTopics: any[] = [];
    if (linkedArticles && linkedArticles.length > 0) {
      const localTopicIds = Array.from(new Set(linkedArticles.map((a: any) => a.local_topic_id)));

      if (localTopicIds.length > 0) {
        const { data: topics } = await supabase!
          .from("mvp2_topics")
          .select("id, stances, category, thumbnail_url")
          .in("id", localTopicIds);
        localTopics = topics || [];
      }
    }

    // Pick a thumbnail from local topics if global doesn't have one
    let thumbnail_url = data.thumbnail_url;
    if (!thumbnail_url && localTopics.length > 0) {
      // Try to find one with a thumbnail
      const withThumb = localTopics.find(t => t.thumbnail_url);
      if (withThumb) thumbnail_url = withThumb.thumbnail_url;
    }

    // 2. Aggregate stance article IDs from all local topics
    const aggregatedStancesRaw = { factual: [] as any[], critical: [] as any[], supportive: [] as any[] };

    // Also include the global topic's own stances if they exist
    const globalStances = (data as any).stances || {};
    if (globalStances.factual) aggregatedStancesRaw.factual.push(...globalStances.factual);
    if (globalStances.critical) aggregatedStancesRaw.critical.push(...globalStances.critical);
    if (globalStances.supportive) aggregatedStancesRaw.supportive.push(...globalStances.supportive);

    if (localTopics) {
      localTopics.forEach((topic: any) => {
        const s = topic.stances || {};
        if (s.factual) aggregatedStancesRaw.factual.push(...s.factual);
        if (s.critical) aggregatedStancesRaw.critical.push(...s.critical);
        if (s.supportive) aggregatedStancesRaw.supportive.push(...s.supportive);
      });
    }

    // Deduplicate IDs
    aggregatedStancesRaw.factual = Array.from(new Set(aggregatedStancesRaw.factual));
    aggregatedStancesRaw.critical = Array.from(new Set(aggregatedStancesRaw.critical));
    aggregatedStancesRaw.supportive = Array.from(new Set(aggregatedStancesRaw.supportive));

    // Collect all IDs to fetch
    const allStanceArticleIds = [
      ...aggregatedStancesRaw.factual,
      ...aggregatedStancesRaw.critical,
      ...aggregatedStancesRaw.supportive
    ];

    let related_articles: any[] = [];
    let articlesData: any[] = [];

    try {
      // 1. Fetch articles directly linked to this global topic
      const { data: directArticles } = await supabase!
        .from("mvp2_articles")
        .select("id, title_original, title_ko, url, source_name, published_at, country_code, global_topic_id")
        .eq("global_topic_id", data.id)
        .order("published_at", { ascending: false })
        .limit(1000);

      // 2. Fetch articles from aggregated stances (if any)
      let stanceArticles: any[] = [];
      if (allStanceArticleIds.length > 0) {
        const { data: sArticles } = await supabase!
          .from("mvp2_articles")
          .select("id, title_original, title_ko, url, source_name, published_at, country_code, global_topic_id")
          .in("id", allStanceArticleIds)
          .order("published_at", { ascending: false });
        stanceArticles = sArticles || [];
      }

      // Merge and deduplicate
      const allArticles = [...(directArticles || []), ...stanceArticles];
      const uniqueArticles = new Map();
      allArticles.forEach(a => uniqueArticles.set(a.id, a));
      articlesData = Array.from(uniqueArticles.values());

      // Filter for related_articles (only those directly linked to global topic)
      related_articles = articlesData
        .filter((a: any) => a.global_topic_id === data.id)
        .slice(0, 40) // Limit related articles list
        .map((a: any) => ({
          id: a.id,
          title: a.title_ko ?? a.title_original,
          url: a.url,
          source: a.source_name,
          country_code: a.country_code,
          title_original: a.title_original,
          title_ko: a.title_ko,
          published_at: a.published_at
        }));

    } catch {
      related_articles = (data as any).related_articles ?? [];
    }

    // Transform stances from DB (JSON with IDs) to Frontend (Array of Objects)
    const articlesMap = new Map(articlesData.map(a => [a.id, a]));
    const stances: any[] = [];

    // Create a map of ID -> Stance Type
    const stanceTypeMap = new Map<string, "POSITIVE" | "NEGATIVE" | "NEUTRAL">();
    aggregatedStancesRaw.supportive.forEach(id => stanceTypeMap.set(id, "POSITIVE"));
    aggregatedStancesRaw.critical.forEach(id => stanceTypeMap.set(id, "NEGATIVE"));
    aggregatedStancesRaw.factual.forEach(id => stanceTypeMap.set(id, "NEUTRAL"));

    // Iterate over ALL fetched articles
    // If an article has a specific stance, use it.
    // If not (but it belongs to this global topic), default to NEUTRAL (Factual) so it shows up in the country list.
    articlesData.forEach(article => {
      const type = stanceTypeMap.get(article.id) || "NEUTRAL";

      // Only add if it's either explicitly stanced OR it belongs to this global topic
      // (The query fetches both, so we just need to be sure)
      if (stanceTypeMap.has(article.id) || article.global_topic_id === data.id) {
        stances.push({
          country_code: article.country_code,
          stance: type,
          one_liner_ko: article.title_ko ?? article.title_original,
          source_link: article.url,
          source_name: article.source_name,
          flag_emoji: getFlagEmoji(article.country_code)
        });
      }
    });

    // 3. Derive category from local topics
    let category = (data as any).category;
    console.log(`[API Debug] Initial category: ${category}`);

    if (!category && localTopics && localTopics.length > 0) {
      console.log(`[API Debug] Found ${localTopics.length} local topics. Checking categories...`);
      const categoryCounts: Record<string, number> = {};
      localTopics.forEach((t: any) => {
        console.log(`[API Debug] Local topic category: ${t.category}`);
        if (t.category) {
          categoryCounts[t.category] = (categoryCounts[t.category] || 0) + 1;
        }
      });

      // Find most frequent category
      let maxCount = 0;
      for (const [cat, count] of Object.entries(categoryCounts)) {
        if (count > maxCount) {
          maxCount = count;
          category = cat;
        }
      }
      console.log(`[API Debug] Derived category: ${category}`);
    } else {
      console.log(`[API Debug] No local topics found or category already exists.`);
      console.log(`[API Debug] linkedArticles count: ${linkedArticles?.length}`);
    }

    const result = {
      topic_id: data.id,
      title: data.title_ko ?? data.topic_name ?? "",
      title_en: data.title_en ?? "",
      intro_ko: data.intro_ko ?? "",
      intro_en: data.intro_en ?? "",
      thumbnail_url: thumbnail_url || null,
      ai_summary: data.ai_summary || null,
      editor_comment: data.editor_comment || null,
      category: category || null,
      article_count: data.article_count ?? 0,
      country_count: data.country_count ?? 0,
      countries: data.countries ?? [],
      keywords: data.keywords ?? [],
      stances: stances,
      perspectives: [],
      related_articles,
      articles: articlesData // Assuming articlesData is the intended 'articles'
    };

    return NextResponse.json(result, { status: 200 });
  } catch (err) {
    console.error("GET /api/global/insights/:id failed", err);
    const mock = await readVsCard();
    return NextResponse.json(mock, { status: 200 });
  }
}
