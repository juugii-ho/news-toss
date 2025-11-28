import { NextRequest, NextResponse } from 'next/server';
import { getSupabaseClient, isSupabaseConfigured } from '@/lib/supabase';

export const dynamic = 'force-dynamic';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const searchParams = request.nextUrl.searchParams;
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '20');
    const country = searchParams.get('country');
    const stance = searchParams.get('stance');

    const offset = (page - 1) * limit;

    if (!isSupabaseConfigured()) {
      return NextResponse.json(
        { error: 'Supabase not configured' },
        { status: 503 }
      );
    }

    const supabase = getSupabaseClient();

    // Build query
    let query = supabase
      .from('mvp_articles')
      .select('*, title_kr', { count: 'exact' })
      .eq('topic_id', id)
      .order('published_at', { ascending: false })
      .range(offset, offset + limit - 1);

    if (country) {
      query = query.eq('country_code', country);
    }

    if (stance) {
      query = query.eq('stance', stance);
    }

    const { data: articles, count, error } = await query;

    if (error) {
      return NextResponse.json(
        { error: 'Failed to fetch articles', details: error.message },
        { status: 500 }
      );
    }

    const totalPages = count ? Math.ceil(count / limit) : 0;

    return NextResponse.json({
      data: articles || [],
      pagination: {
        page,
        limit,
        total: count || 0,
        totalPages,
        hasMore: page < totalPages,
      },
    });
  } catch (error) {
    console.error('Unexpected error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
