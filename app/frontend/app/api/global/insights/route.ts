import { NextResponse } from "next/server";
import { supabase } from "@/lib/supabase-client";
import { readGlobalList } from "@/lib/mock";

export const revalidate = 3600; // 1시간 ISR

export async function GET() {
  // Supabase 연결이 없으면 목업 반환
  if (!supabase) {
    const mock = await readGlobalList();
    return NextResponse.json(mock.items, { status: 200 });
  }

  try {
    const { data: latest } = await supabase
      .from("mvp2_megatopics")
      .select("created_at")
      .order("created_at", { ascending: false })
      .limit(1)
      .maybeSingle();

    if (!latest?.created_at) {
      const mock = await readGlobalList();
      return NextResponse.json(mock.items, { status: 200 });
    }

    const { data, error } = await supabase
      .from("mvp2_megatopics")
      .select("*")
      .eq("created_at", latest.created_at)
      .order("rank", { ascending: true, nullsLast: true })
      .order("article_count", { ascending: false })
      .limit(15);

    if (error) throw error;

    const mapped =
      data?.map((topic: any) => ({
        id: topic.id,
        title_ko: topic.title_ko ?? topic.title ?? "",
        title_en: topic.title_en ?? "",
        intro_ko: topic.intro_ko ?? "",
        intro_en: topic.intro_en ?? "",
        article_count: topic.article_count ?? 0,
        country_count: topic.country_count ?? 0,
        rank: topic.rank,
        is_pinned: topic.is_pinned ?? false,
        hero_image_url: topic.hero_image_url ?? null,
        hot_topic_badge: topic.hot_topic_badge ?? null
      })) ?? [];

    return NextResponse.json(mapped, { status: 200 });
  } catch (err) {
    console.error("GET /api/global/insights failed", err);
    const mock = await readGlobalList();
    return NextResponse.json(mock.items, { status: 200 });
  }
}
