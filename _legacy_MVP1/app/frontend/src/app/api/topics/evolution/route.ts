import { getSupabaseClient } from '@/lib/supabase'
import { NextResponse } from 'next/server'

/**
 * GET /api/topics/evolution
 *
 * Returns summary of topic evolution for today
 * - How many new topics appeared
 * - How many topics continued from yesterday
 * - Average drift score
 * - Total topics tracked
 */
export async function GET(request: Request) {
  try {
    const supabase = getSupabaseClient()
    const { searchParams } = new URL(request.url)
    const date = searchParams.get('date') || new Date().toISOString().split('T')[0]

    // Get today's history records
    const { data: todayHistory, error: todayError } = await supabase
      .from('mvp_topic_history')
      .select('*')
      .eq('date', date)

    if (todayError) {
      console.error('Error fetching today history:', todayError)
      return NextResponse.json({ error: todayError.message }, { status: 500 })
    }

    if (!todayHistory || todayHistory.length === 0) {
      return NextResponse.json({
        date,
        summary: {
          total: 0,
          new: 0,
          continued: 0,
          avg_drift: null,
        },
        topics: [],
      })
    }

    // Calculate statistics
    const newTopics = todayHistory.filter(t => t.is_new_topic === true)
    const continuedTopics = todayHistory.filter(t => t.is_new_topic === false)

    const driftScores = todayHistory
      .filter(t => t.drift_score !== null)
      .map(t => t.drift_score)

    const avgDrift = driftScores.length > 0
      ? driftScores.reduce((a, b) => a + b, 0) / driftScores.length
      : null

    // Categorize by drift (for badges)
    const breaking = continuedTopics.filter(t => t.drift_score && t.drift_score > 0.15)
    const evolving = continuedTopics.filter(t => t.drift_score && t.drift_score > 0.05 && t.drift_score <= 0.15)
    const ongoing = continuedTopics.filter(t => t.drift_score && t.drift_score <= 0.05)

    // Get category distribution
    const categoryDistribution = [1, 2, 3, 4, 5].map(cat => ({
      category: cat,
      count: todayHistory.filter(t => t.category === cat).length,
    }))

    return NextResponse.json({
      date,
      summary: {
        total: todayHistory.length,
        new: newTopics.length,
        continued: continuedTopics.length,
        breaking: breaking.length,
        evolving: evolving.length,
        ongoing: ongoing.length,
        avg_drift: avgDrift ? parseFloat(avgDrift.toFixed(4)) : null,
      },
      category_distribution: categoryDistribution,
      topics: todayHistory.map(t => ({
        id: t.topic_id,
        title_en: t.title_en,
        title_kr: t.title_kr,
        is_new: t.is_new_topic,
        drift_score: t.drift_score,
        intensity: t.intensity,
        category: t.category,
        status: t.status,
        article_count: t.article_count,
        country_count: t.country_count,
        countries: t.countries,
        avg_stance_score: t.avg_stance_score,
      })),
    })
  } catch (error) {
    console.error('Error in /api/topics/evolution:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
