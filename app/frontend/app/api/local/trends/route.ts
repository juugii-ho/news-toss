import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase-client";
import { readLocalList } from "@/lib/mock";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const country = searchParams.get("country") || "KR";
  const page = Number(searchParams.get("page") || "1");
  const limit = Math.min(Number(searchParams.get("limit") || "20"), 50);
  const from = (page - 1) * limit;
  const to = from + limit - 1;

  if (!supabase) {
    const mock = await readLocalList();
    return NextResponse.json(mock, { status: 200 });
  }

  try {
    const { data: topics, error, count } = await supabase
      .from("mvp2_topics")
      .select("*", { count: "exact" })
      .eq("country_code", country)
      .eq("is_published", true)
      .order("article_count", { ascending: false })
      .order("created_at", { ascending: false })
      .range(from, to);

    if (error) throw error;

    const computed = (topics || []).map((topic, idx, arr) => {
      if (topic.display_level) return topic;
      const total = arr.length;
      const lv1 = Math.floor(total * 0.2);
      const lv2 = Math.floor(total * 0.5);
      let display_level: 1 | 2 | 3 = 3;
      if (idx < lv1) display_level = 1;
      else if (idx < lv2) display_level = 2;
      return { ...topic, display_level };
    });

    const hasNextPage = count ? to + 1 < count : topics.length === limit;

    return NextResponse.json(
      {
        country_code: country,
        items: computed.map((topic) => {
          const category = ((topic as any).category || "").toLowerCase();
          const topicIds = (topic as any).topic_ids;
          const isGlobal =
            (Array.isArray(topicIds) && topicIds.length > 0) ||
            (topic.country_code && topic.country_code !== country) ||
            (topic.source_count ?? 0) > 5 ||
            (topic.country_count ?? 0) >= 3 ||
            category.includes("world") ||
            category.includes("international");

          return {
            topic_id: topic.id || (topic as any).topic_id || topic.topic_name || `${country}-${topic.created_at}`,
            title: topic.headline || topic.topic_name || "",
            keyword:
              topic.keywords && topic.keywords.length > 0
                ? topic.keywords[0]
                : topic.topic_name || topic.headline || "",
            keywords: topic.keywords || [],
            article_count: topic.article_count ?? 0,
            display_level: topic.display_level as 1 | 2 | 3,
            media_type: topic.thumbnail_url ? "IMAGE" : "NONE",
            media_url: topic.thumbnail_url || null,
            stances: topic.stances ?? [],
            category: (topic as any).category ?? null,
            is_global: isGlobal,
            summary: topic.summary || "",
            created_at: topic.created_at
          };
        }),
        page,
        total_count: count ?? computed.length,
        limit,
        hasNextPage
      },
      { status: 200 }
    );
  } catch (err) {
    console.error("GET /api/local/trends failed", err);
    const mock = await readLocalList();
    return NextResponse.json(mock, { status: 200 });
  }
}
