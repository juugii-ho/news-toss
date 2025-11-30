import { NextResponse } from "next/server";
import { supabase } from "@/lib/supabase-client";
import { readLocalList } from "@/lib/mock";

export const revalidate = 600; // Revalidate every 10 minutes

type Params = { params: { id: string } };

export async function GET(_req: Request, { params }: Params) {
  const id = params.id;

  if (!id) {
    return NextResponse.json({ error: "Topic ID is required" }, { status: 400 });
  }

  if (!supabase) {
    const mock = await readLocalList();
    const found = mock.items.find((i) => i.topic_id === id);
    if (!found) return NextResponse.json({ error: "Topic not found" }, { status: 404 });
    return NextResponse.json(found, { status: 200 });
  }

  try {
    const { data: topicData, error: topicError } = await supabase
      .from("mvp2_topics")
      .select("*")
      .eq("id", id)
      .maybeSingle();

    if (topicError) throw topicError;
    if (!topicData) {
      return NextResponse.json({ error: "Topic not found" }, { status: 404 });
    }

    const { data: articlesData, error: articlesError } = await supabase
      .from("mvp2_articles")
      .select("id, title_original, title_ko, source_name, published_at, url, global_topic_id, country_code")
      .eq("local_topic_id", id)
      .order("published_at", { ascending: false })
      .limit(50);

    if (articlesError) throw articlesError;

    const keywords = Array.isArray((topicData as any).keywords)
      ? (topicData as any).keywords
      : [];

    // Transform stances from DB (JSON with IDs) to Frontend (Array of Objects)
    const stancesRaw = (topicData as any).stances || { factual: [], critical: [], supportive: [] };
    const articlesMap = new Map((articlesData || []).map(a => [a.id, a]));
    const stances: any[] = [];

    const addStances = (ids: any[], type: string) => {
      if (!Array.isArray(ids)) return;
      ids.forEach(id => {
        const article = articlesMap.get(id);
        if (article) {
          stances.push({
            country_code: article.country_code,
            stance: type,
            one_liner_ko: article.title_ko ?? article.title_original,
            source_link: article.url,
            source_name: article.source_name
          });
        }
      });
    };

    addStances(stancesRaw.supportive, "POSITIVE");
    addStances(stancesRaw.critical, "NEGATIVE");
    addStances(stancesRaw.factual, "NEUTRAL");

    const responseData = {
      topic_id: topicData.id ?? topicData.topic_id,
      title: topicData.headline ?? topicData.topic_name ?? "",
      keyword: keywords[0] ?? topicData.topic_name ?? "",
      article_count: topicData.article_count ?? 0,
      display_level: (topicData.display_level as 1 | 2 | 3) ?? 3,
      media_type: (topicData as any).thumbnail_url ? "IMAGE" : "NONE",
      media_url: (topicData as any).thumbnail_url ?? null,
      stances: stances,
      keywords: keywords.length ? keywords : undefined,
      category: (topicData as any).category ?? null,
      country_code: (topicData as any).country_code ?? null,
      global_topic_id: (topicData as any).global_topic_id ?? undefined,
      ai_summary: (topicData as any).ai_summary ?? null,
      articles: (articlesData || []).map((article) => ({
        id: article.id,
        title: article.title_ko ?? article.title_original,
        title_ko: article.title_ko,
        title_original: article.title_original,
        country_code: article.country_code,
        source: article.source_name,
        published_at: article.published_at,
        url: article.url,
        global_topic_id: article.global_topic_id
      }))
    };

    return NextResponse.json(responseData, { status: 200 });
  } catch (err: any) {
    console.error(`GET /api/local/topics/${id} failed`, err);
    const mock = await readLocalList();
    const found = mock.items.find((i) => i.topic_id === id);
    if (!found) return NextResponse.json({ error: "Not Found" }, { status: 404 });
    return NextResponse.json(found, { status: 200 });
  }
}
