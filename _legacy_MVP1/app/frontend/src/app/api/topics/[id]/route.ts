import { NextRequest, NextResponse } from 'next/server';
import { getSupabaseClient, isSupabaseConfigured } from '@/lib/supabase';

export const dynamic = 'force-dynamic';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;

    // Check if Supabase is configured
    if (!isSupabaseConfigured()) {
      return NextResponse.json(
        {
          error: 'Supabase not configured',
          message: 'Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY',
        },
        { status: 503 }
      );
    }

    const supabase = getSupabaseClient();

    // Fetch topic
    const { data: topic, error: topicError } = await supabase
      .from('mvp_topics')
      .select('*')
      .eq('id', id)
      .single();

    if (topicError || !topic) {
      return NextResponse.json(
        { error: 'Topic not found', details: topicError?.message },
        { status: 404 }
      );
    }

    // Fetch articles if requested (default to true for detail, but we limit to 5 for preview performance)
    const searchParams = request.nextUrl.searchParams;
    const includeArticles = searchParams.get('include_articles') !== 'false';
    let articles: any[] = [];

    if (includeArticles) {
      const { data: fetchedArticles, error: articlesError } = await supabase
        .from('mvp_articles')
        .select('id, title, title_kr, url, source, country_code, published_at, stance, stance_score, embedding, topic_id, created_at')
        .eq('topic_id', id)
        .order('stance_score', { ascending: false })
        .limit(50); // Fetch more to ensure we have diversity

      if (articlesError) {
        console.error('Error fetching articles:', articlesError);
      } else if (fetchedArticles) {
        // Group by stance
        const supportive = fetchedArticles.filter(a => a.stance === 'Supportive');
        const factual = fetchedArticles.filter(a => a.stance === 'Factual');
        const critical = fetchedArticles.filter(a => a.stance === 'Critical');
        const others = fetchedArticles.filter(a => !['Supportive', 'Factual', 'Critical'].includes(a.stance));

        // Select 1-2 from each if available to form a set of 5
        // User requested: "One random article per stance"
        // We will try to get at least 1 from each, then fill the rest.

        const selected: any[] = [];
        const pickRandom = (arr: any[]) => arr.length > 0 ? arr[Math.floor(Math.random() * arr.length)] : null;

        // 1. Pick one from each stance
        const s1 = pickRandom(supportive);
        const f1 = pickRandom(factual);
        const c1 = pickRandom(critical);

        if (s1) selected.push(s1);
        if (f1) selected.push(f1);
        if (c1) selected.push(c1);

        // 2. Fill the rest (up to 5) from remaining unique articles
        const remaining = fetchedArticles.filter(a => !selected.find(s => s.id === a.id));

        // Shuffle remaining to get random fill
        for (let i = remaining.length - 1; i > 0; i--) {
          const j = Math.floor(Math.random() * (i + 1));
          [remaining[i], remaining[j]] = [remaining[j], remaining[i]];
        }

        while (selected.length < 5 && remaining.length > 0) {
          selected.push(remaining.pop());
        }

        articles = selected;
      }
    }

    // Fetch stats for this topic
    const { data: stats, error: statsError } = await supabase
      .from('mvp_topic_country_stats')
      .select('*')
      .eq('topic_id', id);

    if (statsError) {
      console.error('Error fetching stats:', statsError);
      return NextResponse.json(
        { error: 'Failed to fetch topic statistics', details: statsError.message },
        { status: 500 }
      );
    }

    // Calculate totals
    const total_supportive = stats?.reduce((sum, s) => sum + (s.supportive_count || 0), 0) || 0;
    const total_factual = stats?.reduce((sum, s) => sum + (s.factual_count || 0), 0) || 0;
    const total_critical = stats?.reduce((sum, s) => sum + (s.critical_count || 0), 0) || 0;
    const article_count = total_supportive + total_factual + total_critical;
    const countries_involved = stats?.map((s) => s.country_code) || [];

    return NextResponse.json({
      data: {
        ...topic,
        stats: stats || [],
        articles: articles, // Return fetched articles (limited to 5)
        countries_involved,
        article_count,
        total_supportive,
        total_factual,
        total_critical,
      },
    });
  } catch (error) {
    console.error('Unexpected error in /api/topics/[id]:', error);
    return NextResponse.json(
      {
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
