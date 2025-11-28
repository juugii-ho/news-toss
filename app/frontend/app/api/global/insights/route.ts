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
    const { data, error } = await supabase
      .from("MVP2_global_topics")
      .select(
        `
        id,
        title_ko,
        title_en,
        intro_ko,
        intro_en,
        article_count,
        country_count,
        rank,
        is_pinned,
        perspectives:MVP2_perspectives(
          country_code,
          stance,
          one_liner_ko,
          one_liner_en,
          source_link,
          country:MVP2_countries(
            name_ko,
            name_en,
            flag_emoji
          )
        )
      `
      )
      .order("is_pinned", { ascending: false })
      .order("rank", { ascending: true, nullsLast: true })
      .order("article_count", { ascending: false })
      .limit(10);

    if (error) throw error;

    return NextResponse.json(
      (data || []).map((topic) => ({
        id: topic.id,
        title_ko: topic.title_ko,
        title_en: topic.title_en,
        intro_ko: topic.intro_ko,
        intro_en: topic.intro_en,
        article_count: topic.article_count,
        country_count: topic.country_count,
        rank: topic.rank,
        is_pinned: topic.is_pinned,
        perspectives: (topic as any).perspectives?.map((p: any) => ({
          country_code: p.country_code,
          country_name_ko: p.country?.name_ko,
          country_name_en: p.country?.name_en,
          flag_emoji: p.country?.flag_emoji,
          stance: p.stance,
          one_liner_ko: p.one_liner_ko,
          one_liner_en: p.one_liner_en,
          source_link: p.source_link
        })) ?? []
      })),
      { status: 200 }
    );
  } catch (err) {
    console.error("GET /api/global/insights failed", err);
    const mock = await readGlobalList();
    return NextResponse.json(mock.items, { status: 200 });
  }
}
