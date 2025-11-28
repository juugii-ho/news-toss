import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { isSupabaseConfigured } from '@/lib/supabase';
import type { TopicWithStats, Article } from '@/lib/supabase';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    // Check if Supabase is configured
    if (!isSupabaseConfigured()) {
      return NextResponse.json(
        {
          error: 'Supabase not configured',
          message: 'Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY',
          fallback: true
        },
        { status: 503 }
      );
    }

    const searchParams = request.nextUrl.searchParams;
    const date = searchParams.get('date');

    // Use service role key for server-side operations to bypass RLS
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
    const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

    if (!supabaseKey) {
      return NextResponse.json({ error: "Service role key missing in env" }, { status: 500 });
    }

    const supabase = createClient(supabaseUrl, supabaseKey);

    // 1. Fetch Topics
    // Explicitly select columns to avoid errors with missing/new columns
    let topicsQuery = supabase
      .from('mvp_topics')
      .select('id, title, title_kr, headline, summary, date, country_count, thumbnail_url, divergence_score, created_at, merged_from_topics')
      .order('date', { ascending: false });

    if (date) {
      topicsQuery = topicsQuery.eq('date', date);
    } else {
      // Default: Get latest topics. 
      // We prioritize 'date' desc, then 'country_count' desc
      const limit = parseInt(searchParams.get('limit') || '500');
      topicsQuery = topicsQuery
        .order('date', { ascending: false })
        .order('country_count', { ascending: false })
        .order('created_at', { ascending: false })
        .limit(limit);
    }

    const { data: topics, error: topicsError } = await topicsQuery;

    if (topicsError) {
      console.error('Error fetching topics:', topicsError);
      return NextResponse.json(
        { error: 'Failed to fetch topics', details: topicsError.message },
        { status: 500 }
      );
    }

    if (!topics || topics.length === 0) {
      return NextResponse.json({ data: [] });
    }

    // 2. Fetch Article Metadata for Aggregation
    // We need to calculate article_count and countries_involved manually
    // because they are not in mvp_topics table.
    const topicIds = topics.map(t => t.id);

    // Fetch minimal data for aggregation: topic_id and country_code
    // We fetch all articles for these topics to aggregate in memory.
    // This is acceptable for MVP scale (~500 topics * ~10 articles = ~5000 rows, lightweight)
    const { data: articlesMeta, error: articlesError } = await supabase
      .from('mvp_articles')
      .select('topic_id, country_code')
      .in('topic_id', topicIds);

    if (articlesError) {
      console.error('Error fetching article metadata:', articlesError);
      // We continue without stats if this fails, to at least show topics
    }

    // 3. Aggregate Stats in Memory
    const statsMap: Record<number, { article_count: number, countries: Set<string> }> = {};

    if (articlesMeta) {
      articlesMeta.forEach((a: any) => {
        if (!statsMap[a.topic_id]) {
          statsMap[a.topic_id] = { article_count: 0, countries: new Set() };
        }
        statsMap[a.topic_id].article_count++;
        if (a.country_code) {
          statsMap[a.topic_id].countries.add(a.country_code);
        }
      });
    }

    // 4. Merge Stats into Topics
    const topicsWithStats: TopicWithStats[] = topics.map((topic: any) => {
      const stats = statsMap[topic.id] || { article_count: 0, countries: new Set() };

      // Fallback for countries: try merged_from_topics or ID parsing
      let countries = Array.from(stats.countries);
      if (countries.length === 0) {
        if (topic.merged_from_topics && Array.isArray(topic.merged_from_topics)) {
          countries = topic.merged_from_topics.map((id: string) => id.split('-')[0]);
        } else {
          // Try parsing ID (e.g. KR-topic-1)
          const parts = topic.id.toString().split('-');
          if (parts.length >= 2 && parts[0].length === 2) {
            countries = [parts[0]];
          }
        }
        // Deduplicate
        countries = Array.from(new Set(countries));
      }

      return {
        ...topic,
        article_count: stats.article_count,
        countries_involved: countries,
        stats: [] // Detailed stats not available in this simplified flow
      };
    }).filter(t => t.article_count > 0); // Filter out ghost topics with no articles

    // Deduplicate by title_kr (keep the one with most articles)
    const uniqueTopicsMap = new Map<string, TopicWithStats>();

    topicsWithStats.forEach(topic => {
      const key = topic.title_kr || topic.title;
      const existing = uniqueTopicsMap.get(key);

      if (!existing || (topic.article_count || 0) > (existing.article_count || 0)) {
        uniqueTopicsMap.set(key, topic);
      }
    });

    const uniqueTopics = Array.from(uniqueTopicsMap.values());

    // 5. Calculate Meta Info
    const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD format
    const todayCount = uniqueTopics.filter(t => t.date === today).length;

    // Sort final results
    uniqueTopics.sort((a, b) => {
      // 1. Date (desc)
      if (a.date !== b.date) return b.date.localeCompare(a.date);
      // 2. Country count (desc)
      if ((b.countries_involved?.length || 0) !== (a.countries_involved?.length || 0)) {
        return (b.countries_involved?.length || 0) - (a.countries_involved?.length || 0);
      }
      // 3. Article count (desc)
      return (b.article_count || 0) - (a.article_count || 0);
    });

    // Get latest timestamp
    const latestUpdate = topics.reduce((latest: Date, topic: any) => {
      const topicTime = new Date(topic.created_at || topic.date);
      return topicTime > latest ? topicTime : latest;
    }, new Date(0));

    return NextResponse.json({
      meta: {
        count: todayCount || 0,
        updatedAt: latestUpdate.toISOString()
      },
      data: uniqueTopics,
      source: `supabase-aggregated (topics: ${topics.length}, articles: ${articlesMeta?.length || 0}, error: ${articlesError?.message}, firstId: ${topics[0]?.id})`
    });

  } catch (error) {
    console.error('Unexpected error in /api/topics:', error);
    return NextResponse.json(
      {
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error',
        fallback: true
      },
      { status: 500 }
    );
  }
}
