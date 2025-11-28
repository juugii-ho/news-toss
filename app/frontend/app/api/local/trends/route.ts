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
    const { data: topics, error, count } = await supabase
      .from("MVP2_local_topics")
      .select("*", { count: "exact" })
      .eq("country_code", country)
      .order("article_count", { ascending: false })
      .order("created_at", { ascending: false })
      .range(from, to);

    if (error) throw error;

    // display_level이 없을 경우 article_count 순서로 계산 (20/30/50% 구간)
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
          topic_id: topic.id,
          title: topic.title,
          keyword: topic.keyword,
          article_count: topic.article_count,
          display_level: topic.display_level,
          media_type: topic.media_type,
          media_url: topic.media_url
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
