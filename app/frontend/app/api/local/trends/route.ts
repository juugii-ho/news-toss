import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase-client";
import { readLocalList } from "@/lib/mock";

export const revalidate = 3600; // 1시간 ISR

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
    // 최신 created_at 배치 선택
    const { data: latest } = await supabase
      .from("mvp2_topics")
      .select("created_at")
      .eq("country_code", country)
      .order("created_at", { ascending: false })
      .limit(1)
      .maybeSingle();

    if (!latest?.created_at) {
      const mock = await readLocalList();
      return NextResponse.json(mock, { status: 200 });
    }

    const { data: topics, error, count } = await supabase
      .from("mvp2_topics")
      .select("*", { count: "exact" })
      .eq("country_code", country)
      .eq("created_at", latest.created_at)
      .order("article_count", { ascending: false })
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

    return NextResponse.json(
      {
        country_code: country,
        topics: computed.map((topic) => ({
          topic_id: topic.id ?? topic.topic_id,
          title: topic.title_ko ?? topic.title ?? "",
          keyword: topic.keyword,
          article_count: topic.article_count ?? 0,
          display_level: topic.display_level as 1 | 2 | 3,
          media_type: (topic.media_type as any) ?? "NONE",
          media_url: topic.media_url ?? null,
          stances: (topic as any).stances ?? []
        })),
        page,
        total_count: count ?? computed.length
      },
      { status: 200 }
    );
  } catch (err) {
    console.error("GET /api/local/trends failed", err);
    const mock = await readLocalList();
    return NextResponse.json(mock, { status: 200 });
  }
}
