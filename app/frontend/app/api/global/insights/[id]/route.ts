import { NextResponse } from "next/server";
import { supabase } from "@/lib/supabase-client";
import { readVsCard } from "@/lib/mock";

export const revalidate = 3600; // 1시간 ISR

type Params = {
  params: { id: string };
};

export async function GET(_req: Request, { params }: Params) {
  const id = params.id;

  if (!supabase) {
    const mock = await readVsCard();
    return NextResponse.json(mock, { status: 200 });
  }

  try {
    const { data, error } = await supabase
      .from("mvp2_megatopics")
      .select("*")
      .eq("id", id)
      .maybeSingle();

    if (error) throw error;
    if (!data) {
      return NextResponse.json({ error: "Not Found", message: "Global insight not found" }, { status: 404 });
    }

    const stances: any[] = Array.isArray((data as any).stances) ? (data as any).stances : [];

    const result = {
      id: data.id,
      title_ko: data.title_ko ?? data.title ?? "",
      title_en: data.title_en ?? "",
      intro_ko: data.intro_ko ?? "",
      intro_en: data.intro_en ?? "",
      article_count: data.article_count ?? 0,
      country_count: data.country_count ?? stances.length,
      perspectives: stances.map((p) => ({
        country_code: p.country_code,
        country_name_ko: p.country_name_ko,
        country_name_en: p.country_name_en,
        flag_emoji: p.flag_emoji,
        stance: p.stance,
        one_liner_ko: p.one_liner_ko,
        one_liner_en: p.one_liner_en,
        source_link: p.source_link
      })),
      related_articles: (data as any).related_articles ?? []
    };

    return NextResponse.json(result, { status: 200 });
  } catch (err) {
    console.error("GET /api/global/insights/:id failed", err);
    const mock = await readVsCard();
    return NextResponse.json(mock, { status: 200 });
  }
}
