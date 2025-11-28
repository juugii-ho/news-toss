import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
const supabase = createClient(supabaseUrl, supabaseKey);

export async function GET(
    request: Request,
    { params }: { params: Promise<{ id: string }> }
) {
    const { id: topicId } = await params;

    try {
        // 1. Find the history record for this topic (today's snapshot)
        // We look for a record in mvp_topic_history where topic_id matches.
        // Ideally, we want the *latest* one.
        const { data: latestHistory, error: historyError } = await supabase
            .from('mvp_topic_history')
            .select('*')
            .eq('topic_id', topicId)
            .order('date', { ascending: false })
            .limit(1)
            .single();

        if (historyError || !latestHistory) {
            // If no history yet (maybe just created today and pipeline hasn't run, or script didn't pick it up),
            // return empty array or just the current topic as a single point?
            // For now, return empty to indicate "no history tracking available yet".
            return NextResponse.json({ timeline: [] });
        }

        // 2. Traverse the chain backwards
        // Since we can't do recursive queries easily in Supabase JS client without a stored procedure,
        // and the chain won't be huge (days), we can fetch by parent_id iteratively or fetch all history for this chain.
        // A better approach for MVP: Fetch ALL history records that might be related?
        // No, that's hard.
        // Iterative approach:

        const timeline = [latestHistory];
        let currentRecord = latestHistory;

        // Limit depth to 30 days
        for (let i = 0; i < 30; i++) {
            if (!currentRecord.parent_topic_id) break;

            const { data: parent, error } = await supabase
                .from('mvp_topic_history')
                .select('*')
                .eq('id', currentRecord.parent_topic_id)
                .single();

            if (error || !parent) break;

            timeline.push(parent);
            currentRecord = parent;
        }

        // Reverse to show oldest first
        timeline.reverse();

        // Calculate insights
        const drifts = timeline.filter(t => t.drift_score !== null).map(t => t.drift_score);
        const maxDrift = drifts.length > 0 ? Math.max(...drifts) : null;
        const avgDrift = drifts.length > 0 ? drifts.reduce((a: number, b: number) => a + b, 0) / drifts.length : null;

        const intensities = timeline.map(t => t.intensity || 0);
        const maxIntensity = Math.max(...intensities);

        const categories = timeline.map(t => t.category || 1);
        const peakCategory = Math.max(...categories);

        return NextResponse.json({
            topic_id: topicId,
            timeline_length: timeline.length,
            first_seen: timeline[0]?.date,
            last_seen: timeline[timeline.length - 1]?.date,
            insights: {
                max_drift: maxDrift ? parseFloat(maxDrift.toFixed(4)) : null,
                avg_drift: avgDrift ? parseFloat(avgDrift.toFixed(4)) : null,
                max_intensity: maxIntensity,
                peak_category: peakCategory,
            },
            timeline,
        });

    } catch (error) {
        console.error('Error fetching timeline:', error);
        return NextResponse.json({ error: 'Failed to fetch timeline' }, { status: 500 });
    }
}
